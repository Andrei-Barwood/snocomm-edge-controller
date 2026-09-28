with open('hil_app.py', 'r') as f:
    content = f.read()

if 'diagnostic_service' not in content:
    content = content.replace(
        'from tan_service import router as tan_router',
        'from tan_service import router as tan_router\nfrom diagnostic_service import router as diagnostic_router'
    )
    content = content.replace(
        'app.include_router(calculator_router)',
        'app.include_router(calculator_router)\napp.include_router(diagnostic_router)'
    )
    with open('hil_app.py', 'w') as f:
        f.write(content)
