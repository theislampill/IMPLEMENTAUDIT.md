# Exact bounded source projection; source module is never imported.
PROFILE='ROOT_SUPPORTED_GITHUB_FETCH_ARTIFACT_LIST_FILE_BROKER_V2'

ARTIFACT_REPRESENTATION='SUPPORTED_COMPLETE_RUN_ARTIFACT_LIST_SELECTED_V1'

KINDS=('run','attempt','jobs','artifact','artifacts','workflow')

TOOL_MAX=4*1024**2

def endpoint(context,artifact_id,kind):
    P.context(context);P.integer(artifact_id,1,10**20);P.need(kind in KINDS,'BROKER_FIXED_KIND')
    run=context['run_id'];prefix='https://api.github.com/repos/'+P.REPOSITORY
    paths={'run':'/actions/runs/'+run,'attempt':'/actions/runs/'+run+'/attempts/1',
      'jobs':'/actions/runs/'+run+'/attempts/1/jobs?per_page=100&page=1',
      'artifact':'/actions/runs/'+run+'/artifacts?per_page=100','artifacts':'/actions/runs/'+run+'/artifacts?per_page=100',
      'workflow':'/contents/'+context['workflow_path']+'?ref='+context['workflow_commit']}
    return prefix+paths[kind]

def unwrap_tool_result(raw,url,*,kind,context=None,workflow_sha256=None,artifact_id=None):
    P.need(kind in KINDS,'BROKER_FIXED_KIND')
    if kind=='workflow':
        P.need(url==V.workflow_endpoint(context),'BROKER_WORKFLOW_ENDPOINT_CONTEXT')
        P.digest(workflow_sha256)
    P.need(type(raw) is bytes and 0<len(raw)<=TOOL_MAX,'BROKER_TOOL_RESULT_BOUND')
    value=V.json_body(raw)
    P.need(type(value) is dict and set(value)<= {'content','structuredContent','isError','_meta'}
      and value.get('isError') is False,'BROKER_TOOL_ERROR_OR_SHAPE')
    meta=value.get('_meta',{})
    P.need(type(meta) is dict and not any(meta.get(k) for k in ('truncated','isTruncated','partial','hasMore')),
      'BROKER_TOOL_TRUNCATION')
    sc=value.get('structuredContent')
    P.need(type(sc) is dict and set(sc)<= {'content','title','modified_date','url','display_url','display_title','structuredContent'}
      and sc.get('url')==url and sc.get('display_url')==url and type(sc.get('content')) is str,
      'BROKER_ACTUAL_TOOL_ENDPOINT')
    if 'structuredContent' in sc:
        inner=sc['structuredContent']
        P.need(type(inner) is dict and set(inner)<= {'title','content','display_url'}
          and inner.get('content')==sc['content'] and inner.get('display_url')==url,'BROKER_NESTED_RESULT_CHANGED')
    body=sc['content'].encode('utf-8')
    P.need(0<len(body)<=P.MAX_METADATA,'BROKER_PROVIDER_BODY_BOUND')
    if kind=='workflow':parsed=V.supported_workflow(body,raw,context,workflow_sha256)
    else:
        parsed=V.json_body(body);P.need(type(parsed) is dict,'BROKER_PROVIDER_BODY_SHAPE')
    if kind=='artifact':
        P.need(url==endpoint(context,artifact_id,'artifact'),'BROKER_ARTIFACT_LIST_ENDPOINT')
        parsed=select_artifact(parsed,artifact_id)
    return body,parsed

def select_artifact(listing,artifact_id):
    """Select an object from a complete genuine listing; never invent an endpoint."""
    P.integer(artifact_id,1,10**20)
    P.need(type(listing) is dict and set(listing)=={'total_count','artifacts'}
      and type(listing['total_count']) is int and type(listing['artifacts']) is list
      and listing['total_count']==len(listing['artifacts'])<=100,'BROKER_ARTIFACT_LIST_COMPLETE')
    seen=set();selected=[]
    for row in listing['artifacts']:
        P.need(type(row) is dict,'BROKER_ARTIFACT_LIST_ROW');P.integer(row.get('id'),1,10**20)
        P.need(row['id'] not in seen,'BROKER_ARTIFACT_LIST_DUPLICATE_ID');seen.add(row['id'])
        if row['id']==artifact_id:selected.append(row)
    P.need(len(selected)==1,'BROKER_ARTIFACT_LIST_UNIQUE_ID');value=selected[0]
    P.need(type(value.get('name')) is str and bool(value['name'])
      and len([r for r in listing['artifacts'] if r.get('name')==value['name']])==1,'BROKER_ARTIFACT_LIST_UNIQUE_NAME')
    return value

def artifact_provenance(raw,url,context,artifact_id):
    body,value=unwrap_tool_result(raw,url,kind='artifact',context=context,artifact_id=artifact_id)
    listing=V.json_body(body)
    return dict(schema='dg16.selected-artifact-list-provenance.v1',authority='NONE',representation=ARTIFACT_REPRESENTATION,
      endpoint=url,run_id=context['run_id'],run_attempt=context['run_attempt'],artifact_id=artifact_id,
      complete_listing_count=listing['total_count'],actual_tool_result=P.descriptor(raw),provider_listing_body=P.descriptor(body),
      selected_artifact_object=P.descriptor(P.encode(value)),direct_artifact_endpoint_used=False,
      authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED')
