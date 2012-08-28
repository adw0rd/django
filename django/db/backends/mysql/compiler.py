try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from django.db.models.sql import compiler


class SQLCompiler(compiler.SQLCompiler):
    distinct_via_group_by = []

    def resolve_columns(self, row, fields=()):
        values = []
        index_extra_select = len(self.query.extra_select)
        for value, field in zip_longest(row[index_extra_select:], fields):
            if (field and field.get_internal_type() in ("BooleanField", "NullBooleanField") and
                value in (0, 1)):
                value = bool(value)
            values.append(value)
        return row[:index_extra_select] + tuple(values)

    def get_distinct(self):
        """MySQL DISTINCT for several fields.
        Implementation in MySQL:
        > SELECT `field1`, `field2`, ..., `fieldN` FROM `table` GROUP BY `field1`, `field2` ORDER BY NULL;
        For a similar statement in PostgreSQL:
        > SELECT DISTINCT ON(`field1`, `field2`) `field1`, `field2`, ..., `fieldN` FROM `table`;
        """
        distinct_fields = super(SQLCompiler, self).get_distinct()
        self.distinct_via_group_by = []
        for field in distinct_fields:
            self.distinct_via_group_by.append(field)
        # Suppression: NotImplementedError("annotate() + distinct(fields) not implemented.")
        return [] if self.query.distinct_fields else None

    def get_grouping(self):
        grouping, gb_params = super(SQLCompiler, self).get_grouping()
        if self.distinct_via_group_by:
            grouping = self.distinct_via_group_by + grouping
        return grouping, gb_params

class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    pass

class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass

class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass

class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass

class SQLDateCompiler(compiler.SQLDateCompiler, SQLCompiler):
    pass
