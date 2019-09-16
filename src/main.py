import argparse
import git
import os
from export_result import ExportResult
from analyze_repo import AnalyzeRepo
from ui.questions import Questions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Path to the repository. Example usage: run.sh path/to/directory')
    parser.add_argument('--output', default='./repo_data.json', dest='output', help='Path to the JSON file that will contain the result')
    parser.add_argument('--skip_obfuscation', default=False, dest='skip_obfuscation', help='If true it won\'t obfuscate the sensitive data such as emails and file names. Mostly for testing purpuse')
    parser.add_argument('--user-identity', default=[], dest='user_identity', help='Specify one user Identity')
    args = parser.parse_args()

    repo = git.Repo(args.directory)
    ar = AnalyzeRepo(repo, args.skip_obfuscation)
    q = Questions()

    print('Initialization...')
    for branch in repo.branches:
        ar.create_commits_entity_from_branch(branch.name)
    ar.flag_duplicated_commits()
    ar.get_commit_stats()
    r = ar.create_repo_entity(args.directory)

    if len(args.user_identity) > 0:
        identities = {
            'user_identity': [args.user_identity]
        }
    else:
        # Ask the user if we cannot find remote URL
        if r.primary_remote_url == '':
            answer = q.ask_primary_remote_url(r)

        identities = q.ask_user_identity(r)
        MAX_LIMIT = 50
        while len(identities['user_identity']) == 0 or len(identities['user_identity']) > MAX_LIMIT:
            if len(identities['user_identity']) == 0:
                print('Please select at least one.')
            if len(identities['user_identity']) > MAX_LIMIT:
                print('You cannot select more than', MAX_LIMIT)
            identities = q.ask_user_identity(r)

    r.local_usernames = identities['user_identity']
    er = ExportResult(r, ignore=True)
    er.export_to_json(args.output)


if __name__ == "__main__":
    main()
