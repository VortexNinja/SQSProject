from typing import Dict
from localstack.aws.api import RequestContext
from localstack.aws.chain import Handler,HandlerChain
from localstack.http import Response
from localstack.services.plugins import SERIALIZERS,StateSerializer
from localstack_ext.utils.cloud_pods import CIRunManager,SyncPodStateManager
class PodStateSyncHandler(Handler):
	def __call__(A,chain,request,response):SyncPodStateManager.get().sync_pod_state()
class CIMetricPublisher(Handler):
	def __call__(A,chain,request,response):CIRunManager.get().publish_metrics()
class StateSerializerHandler(Handler):
	serializers:Dict[str,StateSerializer]
	def __init__(A):A.serializers=SERIALIZERS
	def __call__(C,chain,context,response):
		A=context
		if not A.service:return
		D=A.service.service_name;B=C.serializers.get(D)
		if not B:return
		B.update_state(B.get_context(),A.request)