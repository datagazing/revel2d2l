"""See top level package docstring for documentation"""

import argparse
import collections
import logging
import os
import pathlib
import re
import sys
import tempfile

import Levenshtein
import pandas
import pandasql
import yaml

myself = pathlib.Path(__file__).stem

format = '%(name)s: %(levelname)s: %(funcName)s: %(message)s'
logging.basicConfig(format=format)
logger = logging.getLogger(myself)
logger.setLevel(logging.WARNING)


def main():
    config = configure()
    logger.debug(config)

    logger.info(f"Users lookup file: {config['users']}")
    logger.info(f"Input file: {config['input']}")
    logger.info(f"Output file: {config['output']}")

    # Drop the first and third rows of the Revel input file
    with tempfile.NamedTemporaryFile(suffix='.csv') as tmp:
        logger.debug(f"Temporary file = {tmp.name}")
        lines = open(config['input']).read().split('\n')
        logger.debug(f"Read {len(lines)} lines")

        # Drop the first (index 0) and third (index 2) lines
        # Second line has the variable names (keep)
        # Third line has the max points
        [logger.debug(f"line {i+1}: {j}") for i, j in enumerate(lines[0:4])]
        keep_lines = [lines[1]] + lines[3:]
        open(tmp.name, 'w').write('\n'.join(keep_lines))
        logger.debug(f"Wrote: {tmp.name} ({len(keep_lines)} lines)")
        input = spreadsheet2df(tmp.name)

    logger.debug(f"Input shape: {input.shape}")
    logger.debug(f"Input records:\n{input.head(3)}")
    input['fullname'] = input['First Name'] + ' ' + input['Last Name']
    input = revel_rename(input)
    logger.debug(list(input))

    if not config['users']:
        # If no users file is supplied, summarize Revel input file and exit
        logger.info('No users file provided')
        logger.info('Summarizing Revel input file...')
        cols = list(input)
        cols.remove('fullname')
        cols = [i for i in cols if not i.startswith('Unnamed')]
        logger.info(f"Items: {', '.join(cols[4:])}")
        sys.exit(0)

    users = spreadsheet2df(config['users'])

    logger.debug(f"Users file shape: {users.shape}")
    users['fullname'] = users['First Name'] + ' ' + users['Last Name']
    logger.debug(f"Users records:\n{users.head(3)}")

    output_rows = []

    # Iterate over the users file because we want to create a row for each
    # Even those users that might not have a Revel account yet
    for index, user in users.iterrows():
        name = user['First Name']
        surname = user['Last Name']
        fullname = name + ' ' + surname
        revel_row = match(
            df=input,
            fullname=fullname,
            email=user['Email'],
            threshold=config['similarity'],
        )

        if revel_row is None:
            logger.warning(f"No match for {fullname}")
            logger.warning(f"Setting {fullname} scores all to 0")
            revel_row = {
                k: 0 for k in list(input) if re.search(config['revel'], k)
            }
        else:
            revel_row = {
                k: v for k, v in revel_row.items()
                if re.search(config['revel'], k)
            }

        revel_row = {f"{k} Points Grade": v for k, v in revel_row.items()}

        outrow = dict()
        outrow['OrgDefinedId'] = user['OrgDefinedId']
        outrow['Username'] = user['Username']
        outrow['First Name'] = user['First Name']
        outrow['Last Name'] = user['Last Name']
        outrow = {**outrow, **revel_row}
        outrow['End-of-Line Indicator'] = config['eol']
        logger.debug(f"Output row = {outrow}")
        output_rows.append(outrow)

    # Output file columns:
    # OrgDefinedId Username surname name Assignment End-of-Line Indicator

    output = pandas.DataFrame(output_rows)
    logger.debug(f"Writing output file: '{config['output']}' ...")
    output.to_csv(config['output'], index=False)
    logger.info(f"Shape of output: {output.shape}")
    logger.info(f"Wrote output file: {config['output']}")


def revel_rename(df):
    """Rename revel columns to just the assessment name."""

    logger.debug('Renaming Revel columns')
    for col in list(df):
        if not re.search(r'^\d', col):
            continue
        x = re.split(r'\s*:\s*', col)
        # chapter_num = x[0]
        # topic = x[1]
        # assessment_type = x[2]
        assessment_name = x[3]
        # assessment_topic = x[4]

        logger.debug(f"Renaming '{col}' -> '{assessment_name}' ...")
        df.rename(columns={col: x[3]}, inplace=True)

    return df


def match(df, fullname, email, threshold, lower=True):
    """Search for and return matching row in df as dict."""

    logger.debug(f"Guessing ID for {fullname}...")

    # If email is an exact match, use that

    query = f"select * from df where Email = '{email}'"
    result = pandasql.sqldf(query, locals())
    if len(result) == 1:
        logger.info(f"Matched {fullname} by exact email address")
        i, record = next(result.iterrows())
        record = record.to_dict()
        logger.debug(f"type(record) = {type(record)}")
        logger.debug(record)
        return record

    if lower:
        def compare(row):
            return similar(row['fullname'].lower(), fullname.lower())
    else:
        def compare(row):
            return similar(row['fullname'], fullname)

    df['similarity'] = df.apply(compare, axis=1)

    sorted_df = df.sort_values(by='similarity', ascending=False)

    # Get the top row (which will have the highest similarity score)
    top_row = sorted_df.iloc[0].to_dict()

    if top_row['similarity'] < threshold:
        logger.warning(f"Similarity < {threshold} for {fullname}")
        logger.debug(
            f"Top:\n{sorted_df.head(3)[['fullname', 'similarity']]}"
        )
        return None

    score = top_row['similarity']
    logger.info(f"Matched {fullname} by Levenshtein similarity ({score:.2f})")

    # del df['similarity']
    return top_row


def similar(str1, str2):
    """Compute the similarity of two strings."""
    # logger.debug(f"Comparing: '{str1}', '{str2}'")
    max_len = max(len(str1), len(str2))
    if max_len == 0:
        return 1.0  # Both strings are empty
    return 1 - Levenshtein.distance(str1, str2) / max_len


def spreadsheet2df(filename):
    """Load spreadsheet as dataframe."""
    if False:
        pass  # Kluge to ease reordering of cases
    elif filename.endswith('.csv'):
        df = pandas.read_csv(filename)
    elif filename.endswith('.xlsx'):
        df = pandas.read_excel(filename)
    else:
        raise IOError("Unknown file type/extension: {filename}")
    return df


def configure():
    """Create a ChainMap: command line options, config file."""
    maps = list()
    maps.append({k: v for k, v in vars(cmdline()).items() if v is not None})
    maps.append(yaml_conf())
    # maps.append()  # defaults
    cm = collections.ChainMap(*maps)
    return cm


def cmdline():
    description = 'Convert Revel grades export csv to D2L grades import csv'
    config_file = os.path.expanduser(f"~/.{myself}.yaml")
    epilog = f"""
        Heuristics used to match user records:
        1. Match by email address (exact)
        2. Match by full name string similarity (Levenshtein distance score)
        See -S option for similarity score threshold
        Input file default: 'non-weighted course_assessments download.csv'
        Config file: {config_file}
    """
    epilog = '\n'.join([i.strip() for i in epilog.split('\n') if i != ''])
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    help = 'set loglevel to INFO'
    parser.add_argument('-v', '--verbose', action='store_true', help=help)

    help = 'set loglevel to DEBUG'
    parser.add_argument('-d', '--debug', action='store_true', help=help)

    default = 'non-weighted course_assessments download.csv'
    parser.add_argument(
        '-i', '--input',
        help='Revel grades input csv file (csv)',
        metavar='F',
        type=valid_csv,
        default=default,
    )

    parser.add_argument(
        '-u', '--users',
        help='D2L users file (csv or xlsx; any grade item works)',
        metavar='F',
        type=valid_csv_xlsx,
    )

    default = f"{myself}_out.csv"
    parser.add_argument(
        '-o', '--output',
        help=f"D2L output file (default: {default})",
        metavar='F',
        type=valid_csv,
        default=default,
    )

    parser.add_argument(
        '-S', '--similarity',
        help='Similarity threshold between 0 and 1 (default: .75)',
        metavar='N',
        type=float,
        default=.75,
    )

    parser.add_argument(
        '-E', '--eol',
        help='''D2L end-of-line indicator (default: '#')''',
        metavar='EOL',
        default='#',
    )

    parser.add_argument(
        '-R', '--revel',
        help='''Revel assignments; regex (default: 'Quiz')''',
        metavar='RE',
        default=r'Quiz',
    )

    logfile = f"{myself}_log.txt"
    parser.add_argument(
        '-L', '--Log',
        help=f"Log to file also ({logfile})",
        action='store_true',
    )

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    args.verbose = True if args.debug else args.verbose

    logger.setLevel(logging.INFO) if args.verbose else None
    logger.setLevel(logging.DEBUG) if args.debug else None

    if args.Log:
        logger.addHandler(logging.FileHandler(logfile))

    return args


def valid_csv(filename):
    x = filename.lower()  # Case insensitive filename extension validation
    if not x.endswith('.csv'):
        raise argparse.ArgumentTypeError(f"{filename} mut be csv")
    return filename


def valid_csv_xlsx(filename):
    x = filename.lower()  # Case insensitive filename extension validation
    if not (x.endswith('.csv') or x.endswith('.xlsx')):
        raise argparse.ArgumentTypeError(f"{filename} must be csv or xlsx")
    return filename


def yaml_conf(file=os.path.expanduser(f"~/.{myself}.yaml")):
    return yaml.safe_load(open(file)) if os.path.isfile(file) else dict()


if __name__ == '__main__':
    main()
