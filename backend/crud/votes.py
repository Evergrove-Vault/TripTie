# # backend/crud/votes.py
# from sqlalchemy.orm import Session
# from database.models.models import Vote, trip_members
# from sqlalchemy import select

# def can_user_vote_in_trip(db: Session, user_id: int, place_id: int) -> bool:
#     """
#     Проверяет, может ли пользователь голосовать за место:
#     - место должно быть в городе поездки,
#     - пользователь должен быть участником этой поездки.
#     """
#     query = """
#         SELECT 1
#         FROM places p
#         JOIN trips t ON p.city_id = t.city_id
#         JOIN trip_members tm ON tm.trip_id = t.id
#         WHERE p.id = :place_id
#           AND tm.user_id = :user_id
#     """
#     result = db.execute(query, {"place_id": place_id, "user_id": user_id}).fetchone()
#     return result is not None

# def cast_vote(db: Session, user_id: int, place_id: int, vote: bool):
#     """Сохраняет/обновляет голос пользователя за место."""
#     if not can_user_vote_in_trip(db, user_id, place_id):
#         raise PermissionError("User is not a participant of any trip containing this place")

#     # Удаляем предыдущий голос (если был) — один пользователь = один голос за место
#     db.query(Vote).filter(
#         Vote.participant_id == user_id,
#         Vote.place_id == place_id
#     ).delete()

#     # Создаём новый
#     new_vote = Vote(participant_id=user_id, place_id=place_id, vote=vote)
#     db.add(new_vote)
#     db.commit()
#     db.refresh(new_vote)
#     return new_vote

# def get_place_votes_summary(db: Session, place_id: int):
#     """Возвращает статистику по голосам для места: сколько 'за', 'против'."""
#     result = db.execute("""
#         SELECT 
#             COUNT(*) FILTER (WHERE vote = true) AS votes_for,
#             COUNT(*) FILTER (WHERE vote = false) AS votes_against
#         FROM votes
#         WHERE place_id = :place_id
#     """, {"place_id": place_id}).fetchone()
    
#     return {
#         "place_id": place_id,
#         "votes_for": result.votes_for or 0,
#         "votes_against": result.votes_against or 0,
#         "total": (result.votes_for or 0) + (result.votes_against or 0)
#     }
