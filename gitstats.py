
import sys, getopt
import os
import git
from pathlib import Path

Project_list = []

class Project:
    def __init__(self, name, path, branch):
         self.name = name
         self.path = path
         self.branch = branch
         self.authors = []
         self.total_insertions = 0
         self.total_deletions = 0
         self.total_lines = 0
         self.commit_size = 0

    def init_repo(self):
         self.repo = git.Repo(self.path)
         self.commits = list(self.repo.iter_commits(self.branch))
         self.commit_size = len(self.commits)

    def print_authors(self, file):
        file.write("Project: {}\n".format(self.name))
        print "Project: {}\n".format(self.name)
        file.write('=====================\n')
        file.write('Commits/insertions/deletions/lines\n')
        for author in sorted(self.authors, key=lambda author: author.commits, reverse=True):
            file.write(str(author))
            print str(author)

class Author:
    def __init__(self, name, project):
         self.name = name
         self.project = project
         self.insertions = 0
         self.deletions = 0
         self.lines = 0
         self.commits = 0

    def __str__(self):
        insertion_per = 0
        deletion_per = 0
        if self.project.total_insertions > 0:
            insertion_per = round((self.insertions / (self.project.total_insertions * 1.0) * 100.0), 2)

        if self.project.total_deletions > 0:
            deletion_per = round((self.deletions / (self.project.total_deletions * 1.0) * 100.0), 2)



        return "{}, {}({}%), {}({}%), {}({}%), {}({}%)\n".format(self.name, 
            self.commits, round((self.commits / (self.project.commit_size * 1.0) * 100.0), 2), 
            self.insertions, insertion_per, 
            self.deletions, deletion_per, 
            self.lines, round((self.lines / (self.project.total_lines * 1.0) * 100.0), 2))


def getStats(path, branch, name):
    try:
        project = Project(name, path, branch)
        project.init_repo()
        print "Starting {}".format(path)
        Project_list.append(project)
        authors = {}
        c = 0
        for commit in project.commits:
            c += 1
            if c % 1000 == 0:
                print "{}: {}/{}".format(project.name, c, project.commit_size)
            email = commit.author.email
            if email not in authors:
                authors[email] = Author(email, project)
            author = authors[email]
            author.commits += 1
            for filePath, stats in commit.stats.files.items():
                author.insertions += stats['insertions']
                project.total_insertions += stats['insertions']

                author.deletions += stats['deletions']
                project.total_deletions += stats['deletions']

                author.lines += stats['lines']
                project.total_lines += stats['lines']
        project.authors = [ v for v in authors.values()]
        print "Done {}".format(path)
    except Exception as e:
        print 'error: {}'.format(str(e))
        pass

def main(argv):
    path = argv[0]
    branch = argv[1]
    repos = []
    all_authors = {}
    for dir in next(os.walk(path))[1]:
        repos.append(os.path.join(path, dir))

    f = open("git_stats.txt","w+")
    for repo in repos:
        getStats(repo, branch, repo.split('/')[-1])
    
    projects_total = Project("All", "", "")

    for project in Project_list:
        projects_total.commit_size += project.commit_size
        projects_total.total_insertions += project.total_insertions
        projects_total.total_deletions += project.total_deletions
        projects_total.total_lines += project.total_lines

        for author in project.authors:
            if author.name not in all_authors:
                all_authors[author.name] = Author(author.name, projects_total)
            all_authors[author.name].insertions += author.insertions
            all_authors[author.name].deletions += author.deletions
            all_authors[author.name].lines += author.lines
            all_authors[author.name].commits += author.commits

    projects_total.authors = [ v for v in all_authors.values()]
    projects_total.print_authors(f)
    f.write('\n\n')

    for project in Project_list:
        project.print_authors(f)
        f.write('\n\n')

    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])