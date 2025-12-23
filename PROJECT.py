import psutil
import time

class ProcessManager:
    def show_processes(self):
        print("\n" + "=" * 50)
        print("СПИСОК ПРОЦЕССОВ")
        print("=" * 50)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
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
    
    def kill_process(self):
        print("\n" + "=" * 50)
        print("ЗАВЕРШЕНИЕ ПРОЦЕССА")
        print("=" * 50)
        
        identifier = input("Введите PID или имя: ").strip()
        
        if identifier.isdigit():
            self._kill_by_pid(int(identifier))
        else:
            self._kill_by_name(identifier)
    
    def _kill_by_pid(self, pid):
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            print(f"\nПроцесс: {name} (PID: {pid})")
            confirm = input("Завершить? (y/n): ").lower()
            
            if confirm == 'y':
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                    print(f"Процесс {pid} завершен")
                except:
                    try:
                        proc.kill()
                        print(f"Процесс {pid} принудительно завершен")
                    except:
                        print(f"Не удалось завершить процесс {pid}")
        except:
            print(f"Ошибка")
    
    def _kill_by_name(self, name):
        found_processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    found_processes.append(proc.info)
            except:
                continue
        
        if not found_processes:
            print(f"Процессы с именем '{name}' не найдены")
            return
        
        print(f"\nНайдено процессов: {len(found_processes)}")
        for i, proc in enumerate(found_processes):
            print(f"{i+1}. PID: {proc['pid']}, Имя: {proc['name']}")
        
        if len(found_processes) == 1:
            choice = 1
        else:
            try:
                choice = int(input(f"\nВыберите процесс (1-{len(found_processes)}): "))
                if choice < 1 or choice > len(found_processes):
                    print("Неверный выбор")
                    return
            except:
                print("Введите число")
                return
        
        selected = found_processes[choice-1]
        self._kill_by_pid(selected['pid'])
    
    def monitor_process(self):
        print("\n" + "=" * 50)
        print("МОНИТОРИНГ ПРОЦЕССОВ")
        print("=" * 50)
        
        print("Выберите опцию:")
        print("1. Мониторинг всех процессов")
        print("2. Мониторинг конкретного процесса")
        
        choice = input("Выбор (1-2): ").strip()
        
        if choice == "1":
            self._monitor_all_processes()
        elif choice == "2":
            self._monitor_specific_process()
        else:
            print("Неверный выбор")
    
    def _monitor_all_processes(self):
        print("\n" + "=" * 50)
        print("МОНИТОРИНГ ВСЕХ ПРОЦЕССОВ")
        print("=" * 50)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                continue
        
        for i in range(len(processes)):
            for j in range(i + 1, len(processes)):
                if processes[j]['cpu_percent'] > processes[i]['cpu_percent']:
                    processes[i], processes[j] = processes[j], processes[i]
        
        print("Сбор данных 5 секунд...\n")
        
        for second in range(5):
            print(f"\nСекунда {second + 1}:")
            print(f"{'PID':<8} {'Имя':<15} {'CPU%':<8} {'Память%':<10}")
            print("-" * 45)
            
            count = 0
            for proc in processes[:5]:
                if count >= 5:
                    break
                    
                pid = proc['pid']
                name = proc['name'][:15] if proc['name'] else "N/A"
                cpu = proc['cpu_percent'] if proc['cpu_percent'] else 0
                memory = proc['memory_percent'] if proc['memory_percent'] else 0
                
                print(f"{pid:<8} {name:<15} {cpu:<8.1f} {memory:<10.2f}")
                count += 1
            
            if second < 4:
                time.sleep(1)
    
    def _monitor_specific_process(self):
        try:
            pid_input = input("\nВведите PID процесса: ").strip()
            
            if not pid_input.isdigit():
                print("PID должен быть числом")
                return
            
            pid = int(pid_input)
            
            if pid <= 0:
                print("PID должен быть положительным числом")
                return
            
            proc = psutil.Process(pid)
            name = proc.name()
            
            print(f"\n" + "=" * 50)
            print(f"МОНИТОРИНГ ПРОЦЕССА {pid} ({name})")
            print("=" * 50)
            print("Мониторинг 10 секунд...")
            print(f"{'Время':<8} {'CPU%':<8} {'Память%':<10} {'Память (MB)':<12} {'Потоки':<8}")
            print("-" * 60)
            
            for i in range(10):
                try:
                    cpu = proc.cpu_percent(interval=1)
                    memory_percent = proc.memory_percent()
                    
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss // (1024 * 1024)
                    
                    threads = proc.num_threads()
                    
                    print(f"{i+1} сек:{'':<4} {cpu:<8.1f} {memory_percent:<10.2f} {memory_mb:<12} {threads:<8}")
                    
                except:
                    print(f"Процесс {pid} завершен")
                    break
                    
        except:
            print("Ошибка")

def main():
    pm = ProcessManager()
    
    while True:
        print("\n" + "=" * 50)
        print("УПРАВЛЕНИЕ ПРОЦЕССАМИ")
        print("=" * 50)
        print("1. Показать список процессов")
        print("2. Завершить процесс")
        print("3. Мониторинг процессов")
        print("4. Выход")
        
        choice = input("\nВыбор (1-4): ").strip()
        
        if choice == "1":
            pm.show_processes()
        elif choice == "2":
            pm.kill_process()
        elif choice == "3":
            pm.monitor_process()
        elif choice == "4":
            print("\nВыход...")
            break
        else:
            print("\nНеверный выбор")
            time.sleep(1)

if __name__ == "__main__":
    main()
