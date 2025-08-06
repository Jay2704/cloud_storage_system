import signal
import functools
import threading
import time


class TimeoutError(Exception):
    """Exception raised when a function times out."""
    pass


def timeout(seconds):
    """
    Decorator that raises a TimeoutError if the function takes longer than specified seconds.
    
    Args:
        seconds: Maximum time in seconds before timeout
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                # Thread is still running, timeout occurred
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator


# Alternative implementation using signal (Unix/Linux only)
def timeout_signal(seconds):
    """
    Decorator using signal for timeout (Unix/Linux only).
    More precise but only works on Unix-like systems.
    """
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set the signal handler
            old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Restore the old signal handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            return result
        
        return wrapper
    return decorator 