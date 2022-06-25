_A='params'
import json,logging,os,re,sys
from abc import ABC
from typing import Any,Dict,Set
from localstack.services.plugins import SERVICE_PLUGINS
from localstack.utils.aws import aws_stack
from localstack.utils.files import load_file,save_file
from localstack.utils.json import json_safe
from localstack.utils.strings import camel_to_snake_case
from localstack_ext.bootstrap.pods.servicestate.service_state_types import AccountRegion,ServiceKey
from localstack_ext.persistence.metamodel_mappings import METAMODEL_MAPPINGS
LOG=logging.getLogger(__name__)
GetResourceOperationName=str
ResourceStateMetamodel=Dict[str,Any]
ServiceBackendStateMetamodel=Dict[GetResourceOperationName,ResourceStateMetamodel]
class PodStateMetamodel:
	metamodels:Dict[ServiceKey,ServiceBackendStateMetamodel]
	def __init__(A):A.metamodels={}
	def remove_empty_results(A):
		C=False
		for (D,B) in A.metamodels.items():
			for (E,F) in B.items():
				if list(F.values())in[[[],C],[C,[]],[[]]]:B[E]={}
			A.metamodels[D]={C:A for(C,A)in B.items()if A}
		A.metamodels={C:B for(C,B)in A.metamodels.items()if B}
	def to_dict(C):
		A={}
		for (B,D) in C.metamodels.items():E=A.setdefault(B.account_id,{}).setdefault(B.service,{});E[B.region]=D
		A=json_safe(A);return A
class MetamodelExtractor(ABC):
	def extract_state_metamodel(F):
		G={'cloudwatchlogs':'logs','cognitoidentityserviceprovider':'cognito-idp','dynamodbdocument':'dynamodb','eventbridge':'events','timestreamwrite':'timestream-write','rdsdataservice':'rds-data'};B=PodStateMetamodel();H=SERVICE_PLUGINS.list_loaded_services()
		for (D,I) in METAMODEL_MAPPINGS.items():
			A=D.lower();A=G.get(A)or A
			if A not in H:continue
			for C in active_service_regions(A):
				for (E,J) in I.items():
					K=J.get(_A)
					if K:continue
					try:L=F.get_resource_state(A,C,E);M=ServiceKey.for_region_and_service(C,D);N=B.metamodels.setdefault(M,{});N[E]=L
					except Exception as O:LOG.debug('Unable to extract metamodel for service %s in region %s: %s',A,C,O)
		B.remove_empty_results();return B
	def get_resource_state(A,service,region,operation_name):raise NotImplementedError
class InstanceMetamodelExtractor(MetamodelExtractor):
	def get_resource_state(C,service,region,operation_name):B=aws_stack.connect_to_service(service,region_name=region.region);A=getattr(B,camel_to_snake_case(operation_name))();A.pop('ResponseMetadata',None);return A
class PodMetamodelExtractor(MetamodelExtractor):
	def __init__(A,pod):A.pod=pod
	def get_resource_state(A,service,region,operation_name):raise NotImplementedError
def extract_current_state_metamodel():return InstanceMetamodelExtractor().extract_state_metamodel()
def extract_pod_state_metamodel(pod_zip):return PodMetamodelExtractor(pod_zip).extract_state_metamodel()
def active_service_regions(service):
	A=service;C=SERVICE_PLUGINS.list_loaded_services()
	if A in C:
		D=SERVICE_PLUGINS.get_service_container(A);B=D.service.backend_state_lifecycle
		if B:return B.active_service_regions()
	return set()
def generate_metamodel_mappings(web_dir):
	G='\'" ';C=web_dir;E={};C=os.path.join(C,'web','src')
	for (H,P,I) in os.walk(C):
		for F in I:
			if not F.endswith('.tsx'):continue
			J=os.path.join(H,F);B=load_file(J)
			if'useAwsGetter'not in B:continue
			K='useAwsGetter\\(([^,]+),\\s*([^,)]+)(,\\s*(\\[([^])]+)?\\])[^)]*)?\\)'
			for D in re.findall(K,B):L=D[0].strip().strip(G);M=D[1].strip().strip(G);A=D[3].strip().replace('\n',' ');A=[B.strip().split(':')[0]for B in A.strip('[{}] ').split(',')];A=[B for B in A if B];N=E.setdefault(L,{});N[M]={_A:A}
	B=f"# noqa\n# Auto-generated file - DO NOT EDIT\nMETAMODEL_MAPPINGS = {json.dumps(E,indent=4)}\n";O=os.path.join(os.path.dirname(__file__),'metamodel_mappings.py');save_file(O,B)
if __name__=='__main__':
	if len(sys.argv)>2 and sys.argv[1]=='mappings':generate_metamodel_mappings(sys.argv[2])