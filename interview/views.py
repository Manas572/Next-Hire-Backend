from rest_framework.decorators import api_view 
from .models import InterviewQue
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

@api_view(['POST'])
def get_question(request):
    topic=request.data.get('topic')
    difficulty=request.data.get('difficulty')
    used=request.data.get('used_q',[])
    if not difficulty or not topic:
        return Response({"error":"fields are missing" },status=status.HTTP_400_BAD_REQUEST)

    if type(used) is not list:
        return Response({"error":"used questions is not list"},status=status.HTTP_400_BAD_REQUEST)
    
    que=(InterviewQue.objects.filter(topic=topic, difficulty=difficulty).exclude(id__in=used).order_by("?").first())
    if que is None:
        return Response({"missing":"questions completed"},status=status.HTTP_404_NOT_FOUND)
    
    return Response(
        {
            "difficulty":que.difficulty,
            "id":que.id,
            "topic":que.topic,
            "question":que.question,
            "answer":que.answer
        },
        status=status.HTTP_200_OK
    )

    
    


