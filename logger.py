import sys
import os
import traceback
from typing import List

import javalang as javalang

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(cwd, '..', 'perfec2'))

import perfec2

repos_root = '/Users/sroman/repos/'

repos = [
    # 'aa-cfr-api',
    # 'aa-com-api',
    # 'aa-con-api',
    # 'aa-iss-api',
    # 'aa-per-api',
    # 'aa-prl-api',
    # 'address-api',
    # 'ams-search-api',
    # 'apppolicy-api',
    # 'contact-api',
    # 'identifier-api',
    # 'issue-api',
    # 'organization-api',
    # 'organizationgroup-api',
    # 'person-api',
    'role-api',
    # 'tag-api'
    # 'issuesby100m-api',
    # 'issuesby5m-api',
    # 'authorization-api',
    # 'authentication-api'
]


def refactor_classfile(lines: List[str]):
    global cu
    print(f'processing class {cu.types[0].name}')

    # add Logger field
    # todo return added field
    perfec2.add_field(cu.types[0], 'Logger', 'log', 'private', lines, 'Autowired')
    perfec2.field_spacing(perfec2.get_field(cu.types[0], 'log'), lines)

    # remove all @Slf4j
    perfec2.remove_all_anno('Slf4j', lines)

    # add imports:

    perfec2.add_import('org.springframework.beans.factory.annotation.Autowired', cu, lines)
    return perfec2.add_import('org.slf4j.Logger', cu, lines)


def refactor_testfile(lines: List[str]) -> List[str]:
    global cu
    print(f'Refactoring {cu.types[0].name}')

    # add Logger with @Mock
    perfec2.add_field(cu.types[0], 'Logger', 'log', 'private', lines, 'Mock')
    perfec2.field_spacing(perfec2.get_field(cu.types[0], 'log'), lines)

    # check if @InjectMocks required
    if not perfec2.fields_with_anno(cu.types[0], 'InjectMocks'):
        # add @InjectMocks to testee
        perfec2.add_field_annotation(perfec2.find_testee(cu.types[0]), 'InjectMocks', lines)
        perfec2.field_spacing(perfec2.find_testee(cu.types[0]), lines)

        # also add @Before init mocks
        lfield = perfec2.last_field_line(cu.types[0])
        perfec2.add_method('public', 'void', 'init', [], ['MockitoAnnotations.initMocks(this);\n'], lfield + 1, lines, 'Before')

        perfec2.add_import('org.mockito.InjectMocks', cu, lines)
        perfec2.add_import('org.mockito.MockitoAnnotations', cu, lines)
        perfec2.add_import('org.junit.Before', cu, lines)
        perfec2.add_import('org.springframework.beans.factory.annotation.Autowired', cu, lines)

    # add mock import
    perfec2.add_import('org.slf4j.Logger', cu, lines)
    return perfec2.add_import('org.mockito.Mock', cu, lines)


def main():
    global cu

    for repo in repos:
        repo_path = repos_root + repo
        for root, dirs, files in os.walk(repo_path + '/src/'):
            for f in files:
                if f.endswith('.java'):
                    perfec2.process_file(os.path.join(root, f), refactor_classfile, refactor_testfile)

        perfec2.auto.set_entities_version('1.0.0-SNAPSHOT', repo_path)
        perfec2.auto.mvn_clean_compile(repo_path)
        # auto.mvn_clean_test(repo_path)
        # auto.set_entities_version('1.0.0-SNAPSHOT', repo_path)
        # auto.git_add_src_files(repo_path)
        # auto.git_add_test_files(repo_path)


if __name__ == '__main__':
    main()
