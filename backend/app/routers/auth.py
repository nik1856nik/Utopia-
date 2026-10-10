from fastapi import APIRouter, HTTPException, Depends
from ..config import MUNICIPAL_USERS
from ..schemas.auth import LoginRequest, TokenResponse
from ..services.auth import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post('/login', response_model=TokenResponse)
def login(req: LoginRequest):
    email = req.email or (f"{req.employee_id.lower()}@gcc.gov.in" if req.employee_id else None)
    
    # Try finding user by email or employee ID
    user_info = None
    target_email = None
    if email and email in MUNICIPAL_USERS:
        user_info = MUNICIPAL_USERS[email]
        target_email = email
    else:
        # Search by badge_id
        for em, u in MUNICIPAL_USERS.items():
            if req.employee_id and u.get("badge_id", "").lower() == req.employee_id.lower():
                user_info = u
                target_email = em
                break

    if not user_info or user_info["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid official credentials or password.")

    # Department validation if specified
    if req.department and req.department != "Greater Chennai Corporation (Admin)" and req.department not in user_info["department"]:
        if user_info["role"] != "admin":
            raise HTTPException(status_code=403, detail=f"Access denied: You belong to {user_info['department']}")

    token_data = {
        "sub": target_email,
        "email": target_email,
        "name": user_info["name"],
        "role": user_info["role"],
        "department": user_info["department"],
        "designation": user_info["designation"],
        "badge_id": user_info["badge_id"]
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

@router.get('/me')
def get_me(user: dict = Depends(get_current_user)):
    return user
