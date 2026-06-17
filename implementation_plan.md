# JWT Authentication — Implementation Plan

## Overview
Add full JWT-based authentication to MockIQ. Users must **register and login** before accessing any interview feature. The backend issues **access tokens** (15 min) and **refresh tokens** (7 days). The frontend stores tokens in `localStorage` and automatically attaches them to every API request.

`python-jose` is already installed in `pyproject.toml`. Only `passlib[bcrypt]` needs to be added.

---

## Architecture

```
POST /auth/register  → hash password → create user → return tokens
POST /auth/login     → verify password → return tokens
POST /auth/refresh   → validate refresh token → issue new access token
GET  /auth/me        → return current user profile

All /api/v1/* routes → require valid Bearer token in Authorization header
```

---

## Open Questions

> [!IMPORTANT]
> **Token storage**: Tokens will be stored in `localStorage` (simplest for a SPA). If you want `httpOnly` cookies for better XSS protection, please say so.

> [!IMPORTANT]
> **Which routes to protect?** Proposed: **All** interview routes (`/resume`, `/jd`, `/interview`, `/session`, `/answer`, `/report`) require auth. Health check `/health` stays public.

> [!NOTE]
> **Email verification**: Not implemented in V1 — users can log in immediately after registering. Let me know if you want it.

---

## Proposed Changes

### Backend

---

#### [MODIFY] [pyproject.toml](file:///c:/devops/Interview/Backend/pyproject.toml)
Add `passlib[bcrypt]>=1.7.4` to dependencies.

---

#### [MODIFY] [.env](file:///c:/devops/Interview/Backend/.env)
Add new JWT settings:
```
JWT_SECRET_KEY=<random 64-char secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### [MODIFY] [config.py](file:///c:/devops/Interview/Backend/app/core/config.py)
Add `jwt_secret_key`, `jwt_algorithm`, `jwt_access_token_expire_minutes`, `jwt_refresh_token_expire_days` fields.

---

#### [NEW] `app/models/user.py`
```python
class User:
    _id: ObjectId
    email: str          # unique index
    hashed_password: str
    full_name: str
    created_at: datetime
    is_active: bool
```

#### [NEW] `app/repositories/user_repo.py`
- `create(doc)` → insert user
- `get_by_email(email)` → find by email
- `get_by_id(user_id)` → find by ID

#### [NEW] `app/core/security.py`
- `hash_password(plain)` → bcrypt hash
- `verify_password(plain, hashed)` → bcrypt verify
- `create_access_token(data, expires_delta)` → JWT with `sub`, `exp`, `type=access`
- `create_refresh_token(data)` → JWT with `type=refresh`
- `decode_token(token)` → validate & decode, raise on expiry

#### [NEW] `app/schemas/auth.py`
- `RegisterRequest` — email, password, full_name
- `LoginRequest` — email, password
- `TokenResponse` — access_token, refresh_token, token_type, user
- `UserResponse` — id, email, full_name, created_at
- `RefreshRequest` — refresh_token

#### [NEW] `app/services/auth_service.py`
- `register(req)` → check duplicate email → hash → save → return tokens
- `login(req)` → find user → verify password → return tokens
- `refresh(token)` → decode refresh token → issue new access token
- `get_current_user(token)` → decode access token → return user doc

#### [MODIFY] `app/api/deps.py`
Add:
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: DB = Depends(get_database),
) -> dict:
    ...
CurrentUser = Annotated[dict, Depends(get_current_user)]
```

#### [NEW] `app/api/auth.py`
```
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me
```

#### [MODIFY] All API routes (`resume.py`, `jd.py`, `interview.py`, `answer.py`, `report.py`)
Add `current_user: CurrentUser` parameter to each protected endpoint.

#### [MODIFY] `app/database/indexes.py`
Add unique index on `users.email`.

#### [MODIFY] `main.py`
Register `auth.router` under `/api/v1`.

---

### Frontend

---

#### [NEW] `store/authStore.ts`
Zustand store with persist:
- `user`, `accessToken`, `refreshToken`
- `setTokens()`, `clearAuth()`, `isAuthenticated`

#### [MODIFY] `services/api.ts`
- Request interceptor: attach `Authorization: Bearer <accessToken>`
- Response interceptor: on 401, try `POST /auth/refresh` with refresh token → retry original request → on refresh failure, clear auth + redirect to `/login`

#### [NEW] `services/authService.ts`
- `register(email, password, fullName)`
- `login(email, password)`
- `refresh(refreshToken)`
- `me()`

#### [NEW] `types/auth.ts`
TypeScript interfaces for `User`, `TokenResponse`, `LoginRequest`, `RegisterRequest`.

#### [NEW] `components/auth/AuthGuard.tsx`
Client component wrapper — checks `isAuthenticated`, redirects to `/login` if not.

#### [NEW] `app/login/page.tsx`
Login form with email + password, gradient design, link to register.

#### [NEW] `app/register/page.tsx`
Registration form with full name, email, password, confirm password.

#### [MODIFY] `app/layout.tsx`
Wrap layout with `AuthProvider` (TanStack Query `useQuery` for `/auth/me`).

#### [MODIFY] Navbar
Show user avatar/email + logout button when authenticated.

#### [MODIFY] All feature pages
Wrap with `<AuthGuard>` — unauthenticated users redirected to `/login`.

---

## Verification Plan

### Automated Tests
```bash
# Backend
cd Backend && .venv\Scripts\pytest tests/ -v -k "auth"
```

### Manual Verification
1. `POST /api/v1/auth/register` → returns tokens
2. `GET /api/v1/resume/...` without token → 401
3. `GET /api/v1/resume/...` with token → 200
4. Wait for access token to expire → refresh automatically
5. Frontend: register → redirected to dashboard → all features work
6. Logout → redirected to login → API calls return 401
