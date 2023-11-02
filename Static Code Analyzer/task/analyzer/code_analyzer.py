import re
import os
import sys
import ast


def main():
    args = sys.argv
    not_pyfile_template = r".*\.[^p][^y]"
    if len(args) > 2 or re.match(not_pyfile_template, args[1]):
        print("Please call the script with one argument directory or .py file")
    else:
        input_path = args[1]
        if input_path.endswith('.py'):
            sca = StaticCodeAnalyzer(input_path)
            sca.start()
        else:
            for dir_path, dir_names, files in os.walk(input_path):
                for f_name in files:
                    if f_name.endswith('.py'):
                        sca = StaticCodeAnalyzer(input_path+"\\"+f_name)
                        sca.start()


class StaticCodeAnalyzer:
    def __init__(self, path):
        self.path = path
        self.blank_lines = 0

    def start(self):
        self.check_file(self.path)

    def issue_message_printer(self, line_num, code, message):
        print("{}: Line {}: {} {}".format(self.path, line_num, code, message))

    def check_S001(self, line_str, line_nr):
        issue_code = 'S001'
        message = 'Code line is too long (>79 characters)'
        if len(line_str) > 79:
            self.issue_message_printer(line_nr, issue_code, message)

    def check_S002(self, line_str, line_nr):
        issue_code = 'S002'
        message = 'Indentation is not a multiple of four'
        count = 0
        for i in line_str:
            if i == ' ':
                count += 1
            else:
                break
        if count % 4 != 0 and count != 0:
            self.issue_message_printer(line_nr, issue_code, message)

    def check_S003(self, line_str, line_nr):
        issue_code = 'S003'
        message = 'Unnecessary semicolon after a statement'
        template1 = r"^[^#]*;"
        template2 = r".*['\"].*;.*['\"].*"
        if re.match(template1, line_str) and re.match(template2, line_str) is None:
            self.issue_message_printer(line_nr, issue_code, message)

    def check_S004(self, line_str, line_nr):
        issue_code = 'S004'
        message = 'Less than two spaces before inline comments'
        comm_pos = line_str.find('#')
        if comm_pos != -1:  # comm_pos != 0 and comm_pos != -1:
            template1 = r"^[^#]+  #"
            template2 = r"^\s*#+"
            if re.match(template1, line_str) is None and re.match(template2, line_str) is None:
                self.issue_message_printer(line_nr, issue_code, message)

    def check_S005(self, line_str, line_nr):
        issue_code = 'S005'
        message = 'TODO found'
        comm_pos = line_str.find('#')
        if comm_pos != -1:  # comm_pos != 0 and comm_pos != -1:
            template = r".*#.*[t,T][o,O][d,D][o,O].*"
            if re.match(template, line_str) is not None:
                self.issue_message_printer(line_nr, issue_code, message)

    def check_S006(self, line_str, line_nr):
        issue_code = 'S006'
        message = 'More than two blank lines preceding a code line'
        if len(line_str) > 1:
            if self.blank_lines > 2:
                self.issue_message_printer(line_nr, issue_code, message)
            self.blank_lines = 0
        else:
            self.blank_lines += 1
            
    def check_S007(self, line_str, line_nr):
        issue_code = 'S007'
        message = 'Too many spaces after construction_name (def or class)'
        if line_str.find("def") != -1 or line_str.find("class") != -1:
            template1 = r'\s*def \S+\(.*\):'
            template2 = r'\s*class \S+\(?.*\)?:'
            if re.match(template1, line_str) is None and re.match(template2, line_str) is None:
                self.issue_message_printer(line_nr, issue_code, message)
    
    def check_S008(self, tree):
        issue_code = 'S008'
        message = 'Class name should be written in CamelCase'

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                function_name = node.name
                template = r'[A-Z]{1}[A-Za-z]*'
                if re.match(template, function_name) is None:
                    self.issue_message_printer(node.lineno, issue_code, message)
    
    def check_S009(self, tree):
        issue_code = 'S009'
        message = 'Function name function_name should be written in snake_case'
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                template = r'[a-z_]+'
                if re.match(template, function_name) is None:
                    self.issue_message_printer(node.lineno, issue_code, message)

    def check_S010(self, tree):
        issue_code = 'S010'
        message = 'Argument name arg_name should be written in snake_case'
        template = '[a-z_]+'
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [ar.arg for ar in node.args.args]
                for arg_name in args:
                    if re.match(template, arg_name) is None:
                        self.issue_message_printer(node.lineno, issue_code, message)

    def check_S011(self, tree):
        issue_code = 'S011'
        message = 'Variable var_name should be written in snake_case'
        template = '[a-z_]+'
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                fdef_child = ast.iter_child_nodes(node)
                for fdef_node in fdef_child:
                    if isinstance(fdef_node, ast.Assign):
                        as_child = ast.iter_child_nodes(fdef_node)
                        for as_child_node in as_child:
                            if isinstance(as_child_node, ast.Name):
                                if isinstance(as_child_node.ctx, ast.Store):
                                    if re.match(template, as_child_node.id) is None:
                                        self.issue_message_printer(as_child_node.lineno, issue_code, message)

    def check_S012(self, tree):
        issue_code = 'S012'
        message = 'The default argument value is mutable'
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defaults_list = node.args.defaults
                line_nr = node.lineno
                for i in defaults_list:
                    if isinstance(i, ast.List):
                        self.issue_message_printer(line_nr, issue_code, message)
                    elif isinstance(i, ast.Dict):
                        self.issue_message_printer(line_nr, issue_code, message)
                    elif isinstance(i, ast.Set):
                        self.issue_message_printer(line_nr, issue_code, message)
                    else:
                        break

    def check_file(self, file_path):
        file = open(file_path)
        line_num = 0
        tree = ast.parse(file.read())
        file.seek(0)
        for line in file:
            line_num += 1
            self.check_S001(line, line_num)
            self.check_S002(line, line_num)
            self.check_S003(line, line_num)
            self.check_S004(line, line_num)
            self.check_S005(line, line_num)
            self.check_S006(line, line_num)
            self.check_S007(line, line_num)
        self.check_S008(tree)
        self.check_S009(tree)
        self.check_S010(tree)
        self.check_S011(tree)
        self.check_S012(tree)
        file.close()


if __name__ == '__main__':
    main()
