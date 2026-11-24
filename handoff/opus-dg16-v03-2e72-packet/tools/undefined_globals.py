import builtins, symtable, sys
for path in sys.argv[1:]:
    src = open(path, encoding='utf8').read(); top = symtable.symtable(src, path, 'exec')
    defined = {s.get_name() for s in top.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()}
    missing = set()
    def visit(t):
        for s in t.get_symbols():
            if (s.is_global() or (t is top and s.is_referenced())) and s.get_name() not in defined and not hasattr(builtins, s.get_name()):
                missing.add(s.get_name())
        for c in t.get_children(): visit(c)
    visit(top)
    print(path, sorted(missing))
