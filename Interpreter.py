
GO = 0
RET = 1


class Program:
    def __init__(self, read_block, list_base_blocks):
        self.read_block = read_block
        self.base_blocks = list_base_blocks
        self.table_labels = dict()
        self.table_variables = dict()

    def evaluate(self):
        for block in self.base_blocks:
            self.table_labels[block.label] = block

        if not self.base_blocks:
            return None

        self.read_block.evaluate(self.table_variables)

        action = GO
        val = self.base_blocks[0].label
        while action == GO:
            if val not in self.table_labels.keys():
                print("No such label {}".format(val))
                return -1

            try:
                action, val = self.table_labels[val].evaluate(
                    self.table_variables)
            except KeyError:
                print("Variable wasn't declared")
                return -1

        return val


class Read:
    def __init__(self, list_vars):
        self.vars = list_vars

    def evaluate(self, table_variables):
        for var in self.vars:
            value = int(input())
            table_variables[var] = value


class BasicBlock:
    def __init__(self, label, list_assignments, jump):
        self.label = label
        self.assignments = list_assignments
        self.jump = jump

    def evaluate(self, table_variables):
        for assignment in self.assignments:
            assignment.evaluate(table_variables)

        return self.jump.evaluate(table_variables)


class Assignment:
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def evaluate(self, table_variables):
        table_variables[self.var] = self.expr.evaluate(table_variables)


class Jump:
    available_types = ['unconditional', 'condition', 'return']

    def __init__(self, jump_type, *args):
        self.jump_type = jump_type
        if jump_type == 'unconditional':
            self.sub_jump = UnconditionalJump(args[0])

        elif jump_type == 'condition':
            self.sub_jump = ConditionJump(*args)

        elif jump_type == 'return':
            self.sub_jump = ReturnJump(args[0])

        else:
            raise TypeError

    def evaluate(self, table_variables):
        if self.jump_type == 'return':
            action = RET
        else:
            action = GO
        return action, self.sub_jump.evaluate(table_variables)


class ReturnJump:
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, table_variables):
        return self.expr.evaluate(table_variables)


class UnconditionalJump:
    def __init__(self, lab1):
        self.lab1 = lab1

    def evaluate(self, table_variables):
        return self.lab1


class ConditionJump:
    def __init__(self, expr, lab1, lab2):
        self.expr = expr
        self.lab1 = lab1
        self.lab2 = lab2

    def evaluate(self, table_variables):
        if self.expr.evaluate(table_variables):
            return self.lab1
        else:
            return self.lab2


class Expression:
    available_operations = ('*', '+', '-', '==', '>', '<')

    def __init__(self, operand, operation=None, expr=None):
        self.operand = operand
        self.operation = operation
        self.expr = expr

        if ((operation is not None) and
                (operation not in Expression.available_operations)):
            raise TypeError

    def evaluate(self, table_variables):

        if type(self.operand) is str:
            val1 = table_variables[self.operand]
        else:
            val1 = self.operand

        if self.operation is None:
            return val1

        val2 = self.expr.evaluate(table_variables)
        if self.operation == '*':
            return val1 * val2
        elif self.operation == '+':
            return val1 + val2
        elif self.operation == '-':
            return val1 - val2
        elif self.operation == '==':
            return val1 == val2
        elif self.operation == '<':
            return val1 < val2
        elif self.operation == '>':
            return val1 > val2


b1 = BasicBlock(1, [],
                Jump('condition', Expression('x', '==', Expression('y')), 7, 2))

b2 = BasicBlock(2, [],
                Jump('condition', Expression('x', '<', Expression('y')), 5, 3))

b3 = BasicBlock(3, [Assignment('x', Expression('x', '-', Expression('y')))],
                Jump('unconditional', 1))

b5 = BasicBlock(5, [Assignment('y', Expression('y', '-', Expression('x')))],
                Jump('unconditional', 1))

b7 = BasicBlock(7, [], Jump('return', Expression('x')))


blocks = [b1, b2, b3, b5, b7]
program = Program(Read(['x', 'y']), blocks)
print(program.evaluate())
