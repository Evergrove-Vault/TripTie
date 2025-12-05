# # backend/api/votes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from ..database import get_db
# from ..crud.votes import cast_vote, get_place_votes_summary

# router = APIRouter(prefix="/votes", tags=["votes"])

# class VoteRequest(BaseModel):
#     place_id: int
#     vote: bool  # true = за, false = против

# @router.post("/", summary="Проголосовать за/против места")
# def vote(request: VoteRequest, db: Session = Depends(get_db)):
#     try:
#         # TODO: заменить на current_user.id из JWT
#         user_id = 2  # временно 
        
#         vote_obj = cast_vote(db, user_id=user_id, place_id=request.place_id, vote=request.vote)
#         return {
#             "status": "Голос учтён",
#             "data": {
#                 "place_id": vote_obj.place_id,
#                 "vote": vote_obj.vote,
#                 "participant_id": vote_obj.participant_id
#             }
#         }
#     except PermissionError as e:
#         raise HTTPException(status_code=403, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ошибка голосования: {e}")

# @router.get("/{place_id}/summary", summary="Статистика голосов по месту")
# def vote_summary(place_id: int, db: Session = Depends(get_db)):
#     try:
#         summary = get_place_votes_summary(db, place_id)
#         return {
#             "status": "Статистика",
#             "data": summary
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {e}")