from fastapi import HTTPException, status

class FirebaseService:
    async def delete_user(self, firebase_uid: str) -> None:
        try:
            await self.auth.delete_user(firebase_uid)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar usuario de Firebase: {str(e)}"
            ) 