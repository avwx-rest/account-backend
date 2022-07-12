from . import addon, auth, mail, notification, plan, register, stripe, token, user

ROUTERS = [
    addon.router,
    auth.router,
    mail.router,
    notification.router,
    plan.router,
    register.router,
    stripe.router,
    token.router,
    user.router,
]
