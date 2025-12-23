import psutil
import time
import platform

class TaskManager:
    def show_system_info(self):
        print("\n" + "=" * 50)
        print("СИСТЕМНАЯ ИНФОРМАЦИЯ")
        print("=" * 50)
        
        print(f"ОС: {platform.system()} {platform.release()}")
        print(f"Процессор: {platform.processor()}")
        
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        print(f"Ядра: {cpu_count}/{cpu_count_logical}")
        
        print("\nЗагрузка CPU:")
        cpu_percents = psutil.cpu_percent(percpu=True, interval=0.5)
        for i, percent in enumerate(cpu_percents):
            print(f"  Ядро {i+1}: {percent}%")
        
        memory = psutil.virtual_memory()
        print(f"\nПамять: {memory.total // (1024**3)} ГБ")
        print(f"Используется: {memory.percent}%")
        print(f"Доступно: {memory.available // (1024**3)} ГБ")
        
        print("\nДиски:")
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"  {partition.device}: {usage.percent}%")
            except:
                pass
        
        input("\nНажмите Enter...")
    
    def show_processes(self):
        print("\n" + "=" * 50)
        print("СПИСОК ПРОЦЕССОВ")
        print("=" * 50)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                p = proc.info
                processes.append(p)
            except:
                continue
        
        for i in range(len(processes)):
            for j in range(i + 1, len(processes)):
                if processes[j]['memory_percent'] > processes[i]['memory_percent']:
                    processes[i], processes[j] = processes[j], processes[i]
        
        print(f"{'PID':<8} {'Имя':<20} {'CPU%':<8} {'Память%':<10}")
        print("-" * 50)
        
        count = 0
        for p in processes[:25]:
            print(f"{p['pid']:<8} {p['name'][:20]:<20} {p['cpu_percent']:<8.1f} {p['memory_percent']:<10.2f}")
            count += 1
        
        print(f"\nПоказано: {count} процессов")
        input("\nНажмите Enter...")
    
    def process_details(self):
        try:
            pid = int(input("\nВведите PID процесса: "))
            p = psutil.Process(pid)
            
            print(f"\nПроцесс {pid}:")
            print(f"Имя: {p.name()}")
            print(f"Пользователь: {p.username()}")
            print(f"Статус: {p.status()}")
            print(f"CPU: {p.cpu_percent()}%")
            print(f"Память: {p.memory_percent():.2f}%")
            print(f"Потоков: {p.num_threads()}")
            
        except:
            print("Ошибка!")
        
        input("\nНажмите Enter...")
    
    def kill_process(self):
        try:
            pid = int(input("\nВведите PID процесса: "))
            p = psutil.Process(pid)
            
            print(f"\nЗавершить {p.name()} (PID: {pid})?")
            print("1. Да")
            print("2. Нет")
            
            choice = input("Выбор: ")
            
            if choice == "1":
                try:
                    p.terminate()
                    p.wait(timeout=2)
                    print("Завершено")
                except:
                    try:
                        p.kill()
                        print("Принудительно завершено")
                    except:
                        print("Ошибка")
            
        except:
            print("Ошибка!")
        
        input("\nНажмите Enter...")
    
    def monitor(self):
        print("\n" + "=" * 50)
        print("МОНИТОРИНГ")
        print("=" * 50)
        
        print("Сбор данных 5 секунд...\n")
        
        cpu_data = []
        memory_data = []
        
        for i in range(5):
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            
            cpu_data.append(cpu)
            memory_data.append(memory)
            
            print(f"Секунда {i+1}: CPU={cpu}%, Память={memory}%")
        
        avg_cpu = sum(cpu_data) / len(cpu_data)
        avg_memory = sum(memory_data) / len(memory_data)
        
        print(f"\nСреднее: CPU={avg_cpu:.1f}%, Память={avg_memory:.1f}%")
        
        input("\nНажмите Enter...")

def main():
    tm = TaskManager()
    
    while True:
        print("\n" + "=" * 50)
        print("ДИСПЕТЧЕР ЗАДАЧ")
        print("=" * 50)
        print("1. Системная информация")
        print("2. Список процессов")
        print("3. Детали процесса")
        print("4. Завершить процесс")
        print("5. Мониторинг")
        print("6. Выход")
        
        choice = input("\nВыбор (1-6): ")
        
        if choice == "1":
            tm.show_system_info()
        elif choice == "2":
            tm.show_processes()
        elif choice == "3":
            tm.process_details()
        elif choice == "4":
            tm.kill_process()
        elif choice == "5":
            tm.monitor()
        elif choice == "6":
            print("Выход...")
            break
        else:
            print("Неверный выбор!")
            time.sleep(1)

if __name__ == "__main__":
    main()