from src.db.models.comment_model import Comment
from src.dtos.comment_dto import CommentResponseDTO


def to_comment_response(comment: Comment) -> CommentResponseDTO:
    return CommentResponseDTO.model_validate(comment)
