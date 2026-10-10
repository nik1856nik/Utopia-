from fastapi import APIRouter, HTTPException, Depends
from ..config import MUNICIPAL_USERS
from ..schemas.auth import LoginRequest, TokenResponse
from ..services.auth import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post('/login', response_model=TokenResponse)
def login(req: LoginRequest):
    clean_id = (req.employee_id or req.email or "").strip().lower()
    
    # Try finding user by email, badge_id, or alias
    user_info = None
    target_email = None
    
    for em, u in MUNICIPAL_USERS.items():
        aliases = [a.lower() for a in u.get("aliases", [])]
        aliases.extend([em.lower(), u.get("badge_id", "").lower()])
        if clean_id in aliases:
            user_info = u
            target_email = em
            break

    if not user_info or user_info["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid official credentials or password.")

    # Department validation if specified
    if req.department and req.department != "Greater Chennai Corporation (Admin)":
        req_dept_clean = req.department.lower().replace("&", "and").strip()
        user_dept_clean = user_info["department"].lower().replace("&", "and").strip()
        if user_info["role"] != "admin" and (req_dept_clean not in user_dept_clean and user_dept_clean not in req_dept_clean):
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
