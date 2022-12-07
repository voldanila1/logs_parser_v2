import os
import dataclasses
import pathlib
from datetime import datetime
from collections import defaultdict
import argparse


SEP = "','"  # items separator

HEADER = "StartDate','StartTime','EndDate','EndTime','IP','MediaID','SubscriberLogin','device','uTimeStart','uTimeEnd','Organization\n"

STATS_HEADER = "Organization;Counter;Percent\n"

LOG_FILE_MASK = '*.log'


@dataclasses.dataclass
class Record:
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    ip: str
    media_id: str
    subscriber_login: str
    device: str
    unix_time_start: str
    unix_time_end: str
    organization: str

    @property
    def start_datetime(self):
        return datetime.strptime(f'{self.start_date} {self.start_time}', '%Y/%m/%d %H:%M:%S')

    @property
    def end_datetime(self):
        return datetime.strptime(f'{self.end_date} {self.end_time}', '%Y/%m/%d %H:%M:%S')

    def session_duration(self):
        return (self.end_datetime - self.start_datetime).total_seconds()

    def same_org(self, org_name):
        return self.organization == org_name or self.organization.strip('"') == org_name


def make_rec(line):
    return Record(*line.strip().split(SEP))


###

def filter_sessions(min_session, log_files):
    for log_file in log_files:
        tmp_filename = f'{log_file}.tmp'

        with open(tmp_filename, 'w') as f_out:
            f_out.write(HEADER)

            with open(log_file) as f:
                print(log_file)
                f.readline()  # skip header

                for line in f:
                    rec = make_rec(line)
                    if rec.session_duration() > min_session:
                        f_out.write(line)

        os.replace(tmp_filename, log_file)


def filter_orgs(org_name, log_files):
    for log_file in log_files:
        tmp_filename = f'{log_file}.tmp'

        with open(tmp_filename, 'w') as f_out:
            f_out.write(HEADER)

            with open(log_file) as f:
                print(log_file)
                f.readline()  # skip header

                for line in f:
                    rec = make_rec(line)
                    if rec.same_org(org_name):
                        f_out.write(line)

        os.replace(tmp_filename, log_file)


def remove_dup_logins(log_files):
    all_logins = set()

    for log_file in log_files:
        tmp_filename = f'{log_file}.tmp'

        with open(tmp_filename, 'w') as f_out:
            f_out.write(HEADER)

            with open(log_file) as f:
                print(log_file)
                f.readline()  # skip header

                for line in f:
                    rec = make_rec(line)
                    if rec.subscriber_login not in all_logins:
                        all_logins.add(rec.subscriber_login)
                        f_out.write(line)

        os.replace(tmp_filename, log_file)


def stat_orgs(log_files, out_filename):
    counters = defaultdict(int)
    for log_file in log_files:
        with open(log_file) as f:
            print(log_file)
            f.readline()  # skip header
            for line in f:
                rec = make_rec(line)
                counters[rec.organization] += 1

    with open(out_filename, 'w') as f_out:
        f_out.write(STATS_HEADER)
        total = sum(counters.values())
        # sort counters by value in descending order
        sorted_counters = ((k, v) for k, v in sorted(counters.items(), key=lambda item: item[1], reverse=True))
        for org, counter in sorted_counters:
            percent = counter / total * 100
            f_out.write(f"{org};{counter};{percent:.1f}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse access logs. Version 3.")

    subparsers = parser.add_subparsers(dest='subcommand')

    parser_filter_dates = subparsers.add_parser('filter-sessions', help='Filter by session duration.')
    parser_filter_dates.add_argument('min_session', type=int, help='Minimum session duration in seconds.')

    parser_filter_orgs = subparsers.add_parser('filter-orgs', help='Filter by organization name.')
    parser_filter_orgs.add_argument('org_name', type=str, help='Organization name.')

    parser_remove_dup_logins = subparsers.add_parser('remove-dup-logins', help='Remove duplicate subscriber logins.')

    parser_stat_orgs = subparsers.add_parser('stat-orgs', help='Statistics per organization.')
    parser_stat_orgs.add_argument('output', type=str, help='Output file name.')

    parser.add_argument('--logs-dir', type=str, required=True, help='Path to log files.')

    args = parser.parse_args()

    log_files = [p for p in pathlib.Path(args.logs_dir).glob(LOG_FILE_MASK) if p.is_file()]

    if args.subcommand == 'filter-sessions':
        if args.min_session < 0:
            args.error("Minimum session duration is 0 seconds.")
        filter_sessions(args.min_session, log_files)
    elif args.subcommand == 'filter-orgs':
        filter_orgs(args.org_name, log_files)
    elif args.subcommand == 'remove-dup-logins':
        remove_dup_logins(log_files)
    elif args.subcommand == 'stat-orgs':
        stat_orgs(log_files, args.output)
