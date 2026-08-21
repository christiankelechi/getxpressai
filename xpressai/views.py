from django.http import HttpResponse, JsonResponse
from django.db import connection

def landing_page(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Xpress AI - The Future of Intelligent Creation</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
            body {
                font-family: 'Inter', sans-serif;
                background-color: #0f172a;
                color: #f8fafc;
            }
            .gradient-text {
                background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .hero-bg {
                background: radial-gradient(circle at top, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
                            radial-gradient(circle at bottom right, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
            }
            .glass-card {
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        </style>
    </head>
    <body class="min-h-screen flex flex-col hero-bg antialiased relative overflow-hidden">
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div class="absolute top-0 right-1/4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        
        <nav class="w-full px-8 py-6 flex justify-between items-center max-w-7xl mx-auto relative z-10">
            <div class="text-2xl font-extrabold tracking-tighter flex items-center gap-2">
                <span class="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm">X</span>
                Xpress<span class="text-blue-400">AI</span>
            </div>
            <div class="space-x-4">
                <a href="/api/docs/" class="text-sm font-medium text-slate-300 hover:text-white transition">API Docs</a>
                <a href="/admin/" class="text-sm font-medium text-slate-300 hover:text-white transition">Admin</a>
            </div>
        </nav>

        <main class="flex-grow flex flex-col items-center justify-center px-4 text-center relative z-10 mt-10 md:mt-0">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-8">
                <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span> API Services Online
            </div>
            
            <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 max-w-4xl leading-tight">
                The next generation of <br/>
                <span class="gradient-text">Intelligent Automation</span>
            </h1>
            
            <p class="text-lg md:text-xl text-slate-400 max-w-2xl mb-12">
                Xpress AI powers seamless video generation, intelligent conversational models, and advanced biometric security in one highly scalable API ecosystem.
            </p>

            <div class="flex flex-col sm:flex-row gap-4 mb-20">
                <a href="/api/docs/" class="px-8 py-4 rounded-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 text-white font-bold shadow-lg shadow-blue-500/25 transition transform hover:-translate-y-1">
                    Explore the Swagger API
                </a>
                <a href="/redoc/" class="px-8 py-4 rounded-full bg-slate-800 hover:bg-slate-700 text-white font-bold border border-slate-700 transition">
                    View ReDoc Documentation
                </a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full text-left">
                <div class="glass-card p-8 rounded-3xl hover:bg-slate-800/80 transition cursor-default">
                    <div class="w-12 h-12 rounded-2xl bg-pink-500/20 text-pink-400 flex items-center justify-center mb-6">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-white">Video Engine</h3>
                    <p class="text-slate-400 text-sm leading-relaxed">State-of-the-art AI video generation using advanced stable diffusion pipelines and automated narration synthesis.</p>
                </div>
                
                <div class="glass-card p-8 rounded-3xl hover:bg-slate-800/80 transition cursor-default">
                    <div class="w-12 h-12 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center mb-6">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-white">Prompt Models</h3>
                    <p class="text-slate-400 text-sm leading-relaxed">Integrated LLM services via OpenRouter and Gemini, enabling complex chat flows and generative logic directly from the API.</p>
                </div>

                <div class="glass-card p-8 rounded-3xl hover:bg-slate-800/80 transition cursor-default">
                    <div class="w-12 h-12 rounded-2xl bg-purple-500/20 text-purple-400 flex items-center justify-center mb-6">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-white">Advanced Security</h3>
                    <p class="text-slate-400 text-sm leading-relaxed">Built-in face recognition login, robust JWT authentication, and secure user routing for bulletproof data protection.</p>
                </div>
            </div>
        </main>
        
        <footer class="w-full text-center py-8 text-slate-500 text-sm mt-12 relative z-10 border-t border-white/5">
            &copy; 2025 Xpress AI. All rights reserved.
        </footer>
    </body>
    </html>
    """
    return HttpResponse(html_content)

def keep_db_awake(request):
    """
    A lightweight endpoint to ping the database and keep it awake.
    Designed to be hit by Vercel Cron Jobs.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        return JsonResponse({"status": "success", "message": "Database is awake", "result": row})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
