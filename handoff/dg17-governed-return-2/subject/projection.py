def render_report(jobs, profile):
    lines = [profile['heading'], '']
    separator = profile['separator']
    for job in jobs:
        lines.append(separator.join([job['id'], job['label'], job['state']]))
    return '\n'.join(lines) + '\n'
