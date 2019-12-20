import sys
import os
from typing import List

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
    print(f'processing class {perfec2.this_clazz().name}')

    # add Logger field
    # todo return added field
    perfec2.add_field(perfec2.this_clazz(), 'Logger', 'log', 'private', lines, 'Autowired')
    perfec2.field_spacing(perfec2.util.get_field(perfec2.this_clazz(), 'log'), lines)

    # remove all @Slf4j
    perfec2.remove_all_anno('Slf4j', lines)

    # add imports:

    perfec2.add_import('org.springframework.beans.factory.annotation.Autowired', lines)
    return perfec2.add_import('org.slf4j.Logger', lines)


def refactor_testfile(lines: List[str]) -> List[str]:
    print(f'Refactoring {perfec2.this_clazz().name}')

    # add Logger with @Mock
    perfec2.add_field(perfec2.this_clazz(), 'Logger', 'log', 'private', lines, 'Mock')
    log_field = perfec2.util.get_field(perfec2.this_clazz(), 'log')
    perfec2.field_spacing(log_field, lines)

    # check if @InjectMocks required
    if not perfec2.util.fields_with_anno(perfec2.this_clazz(), 'InjectMocks'):
        # add @InjectMocks to testee
        perfec2.add_field_annotation(perfec2.find_testee(perfec2.this_clazz()), 'InjectMocks', lines)
        perfec2.field_spacing(perfec2.find_testee(perfec2.this_clazz()), lines)

        # also add @Before init mocks
        lfield = perfec2.last_field_line(perfec2.this_clazz())
        perfec2.add_method('public', 'void', 'init', [], ['MockitoAnnotations.initMocks(this);\n'], lfield + 1, lines, 'Before')

        perfec2.add_import('org.mockito.InjectMocks', lines)
        perfec2.add_import('org.mockito.MockitoAnnotations', lines)
        perfec2.add_import('org.junit.Before', lines)
        perfec2.add_import('org.springframework.beans.factory.annotation.Autowired', lines)

    # add mock import
    perfec2.add_import('org.slf4j.Logger', lines)
    return perfec2.add_import('org.mockito.Mock', lines)


def main():
    for repo in repos:
        repo_path = repos_root + repo
        for root, dirs, files in os.walk(repo_path + '/src/'):
            for f in files:
                if f.endswith('.java'):
                    perfec2.process_file(os.path.join(root, f), refactor_classfile, refactor_testfile)

        # perfec2.auto.set_entities_version('1.0.0-SNAPSHOT', repo_path)
        # perfec2.auto.mvn_clean_compile(repo_path)
        # auto.mvn_clean_test(repo_path)
        # auto.set_entities_version('1.0.0-SNAPSHOT', repo_path)
        # auto.git_add_src_files(repo_path)
        # auto.git_add_test_files(repo_path)


if __name__ == '__main__':
    main()
