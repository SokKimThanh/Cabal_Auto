import logging
import logging.handlers
import queue
import threading
import time

def worker_thread(logger, thread_id):
    """Function to run in secondary threads to generate log messages."""
    for i in range(3):
        logger.info(f"Message {i+1} from Thread-{thread_id}")
        time.sleep(0.1)

def main():
    # 1. Tạo queue.Queue để chứa log record
    log_queue = queue.Queue()

    # 2. Tạo QueueHandler và cấu hình logger
    queue_handler = logging.handlers.QueueHandler(log_queue)

    # Lấy logger
    logger = logging.getLogger("QueueLogger")
    logger.setLevel(logging.INFO)
    logger.addHandler(queue_handler)

    # 3. Tạo stream handler để in log ra console (sẽ được QueueListener sử dụng)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(threadName)s | %(message)s')
    console_handler.setFormatter(formatter)

    # 4. Tạo QueueListener với StreamHandler
    # QueueListener sẽ đọc các record từ log_queue và đẩy vào console_handler
    queue_listener = logging.handlers.QueueListener(log_queue, console_handler)

    print("Starting QueueListener...")
    queue_listener.start()

    # 5. Chạy một vài thread phụ ghi log vào logger
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_thread, args=(logger, i+1), name=f"Worker-{i+1}")
        t.start()
        threads.append(t)

    # Đợi các thread hoàn thành
    for t in threads:
        t.join()

    print("All worker threads finished. Stopping QueueListener...")

    # Stop the listener to gracefully shutdown logging
    queue_listener.stop()
    print("Main thread done.")

if __name__ == "__main__":
    main()
