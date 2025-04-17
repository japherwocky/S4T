# mcp_cli/commands/chat.py
import os
import typer
import asyncio
from rich import print
from rich.markdown import Markdown
from rich.panel import Panel

# imports
from chat.chat_handler import handle_chat_mode

# app
app = typer.Typer(help="Chat commands")

@app.command("run")
async def chat_run(stream_manager, server_names=None):
    """
    Enter chat mode.
    
    Args:
        stream_manager: StreamManager instance (required)
        server_names: Optional dictionary mapping server indices to their names
    """
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    #os.system("cls" if os.name == "nt" else "clear")
    chat_info_text = (
        "Welcome to the Chat!\n\n"
        f"**Provider:** {provider}  |  **Model:** {model}\n\n"
        "Type 'exit' to quit."
    )
    print(Panel(Markdown(chat_info_text), style="bold cyan", title="Chat Mode", title_align="center"))
    
    try:
        # Create a task for the chat handler
        chat_task = asyncio.create_task(handle_chat_mode(
            stream_manager, 
            provider, 
            model
        ))
        
        # Await the task with proper exception handling
        await chat_task
    except KeyboardInterrupt:
        print("\nChat interrupted by user.")
    except Exception as e:
        print(f"\nError in chat mode: {e}")
    
    # Make sure any pending tasks are properly cancelled
    if 'chat_task' in locals() and not chat_task.done():
        chat_task.cancel()
        try:
            # Give it a short time to cancel gracefully
            await asyncio.wait_for(asyncio.shield(chat_task), timeout=1.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            # Expected when cancelling or timing out
            pass
        except Exception as e:
            # Only print this if it's not a typical cancellation error
            if not isinstance(e, (asyncio.CancelledError, RuntimeError)):
                print(f"Error during chat cleanup: {e}")
    
    # Signal a clean exit to the main process
    return True