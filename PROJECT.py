import psutil
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Generator
from functools import wraps

def header_decorator(title: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("\n" + "=" * 50)
            print(title.center(50))
            print("=" * 50)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    
    def __str__(self):
        return f"{self.pid:<8} {self.name[:20]:<20} {self.cpu_percent:<8.1f} {self.memory_percent:<10.2f}"

class ProcessIterator:
    def __iter__(self):
        self.processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                self.processes.append(ProcessInfo(
                    pid=info['pid'],
                    name=info['name'],
                    cpu_percent=info['cpu_percent'] or 0.0,
                    memory_percent=info['memory_percent'] or 0.0
                ))
            except:
                continue
        self.index = 0
        return self
    
    def __next__(self):
        if self.index < len(self.processes):
            process = self.processes[self.index]
            self.index += 1
            return process
        raise StopIteration

def process_generator():
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            yield ProcessInfo(
                pid=info['pid'],
                name=info['name'],
                cpu_percent=info['cpu_percent'] or 0.0,
                memory_percent=info['memory_percent'] or 0.0
            )
        except:
            continue

class ProcessInterface(ABC):
    @abstractmethod
    def terminate(self) -> bool:
        pass

class ProcessTerminator(ProcessInterface):
    def __init__(self, pid: int):
        self.pid = pid
        try:
            self.proc = psutil.Process(pid)
        except:
            self.proc = None
    
    def terminate(self) -> bool:
        if not self.proc:
            return False
        try:
            self.proc.terminate()
            self.proc.wait(timeout=2)
            return True
        except:
            try:
                self.proc.kill()
                return True
            except:
                return False

class ProcessManager:
    def __init__(self):
        pass
    
    @header_decorator("ВСЕ ПРОЦЕССЫ")
    def show_all_processes(self):
        processes = []
        count = 0
        for proc in process_generator():
            processes.append(proc)
            count += 1
        
        processes.sort(key=lambda x: x.memory_percent, reverse=True)
        
        print(f"{'PID':<8} {'Имя':<20} {'CPU%':<8} {'Память%':<10}")
        print("-" * 50)
        
        for proc in processes[:50]:
            print(proc)
        
        print(f"\nВсего процессов: {count}")
    
    @header_decorator("ЗАВЕРШЕНИЕ ПРОЦЕССА")
    def kill_process(self):
        identifier = input("Введите PID или имя процесса: ").strip()
        
        if identifier.isdigit():
            pid = int(identifier)
            terminator = ProcessTerminator(pid)
            if terminator.terminate():
                print(f"Процесс {pid} завершен")
            else:
                print(f"Не удалось завершить процесс {pid}")
        else:
            self._kill_by_name(identifier)
    
    def _kill_by_name(self, name: str):
        found = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    found.append(proc.info)
            except:
                continue
        
        if not found:
            print(f"Процессы с именем '{name}' не найдены")
            return
        
        print(f"\nНайдено процессов: {len(found)}")
        for i, p in enumerate(found, 1):
            print(f"{i}. PID: {p['pid']}, Имя: {p['name']}")
        
        if len(found) == 1:
            choice = 1
        else:
            try:
                choice = int(input(f"\nВыберите процесс (1-{len(found)}): "))
                if not 1 <= choice <= len(found):
                    print("Неверный выбор")
                    return
            except:
                print("Введите число")
                return
        
        pid = found[choice-1]['pid']
        terminator = ProcessTerminator(pid)
        if terminator.terminate():
            print(f"Процесс {pid} завершен")
        else:
            print(f"Не удалось завершить процесс {pid}")
    
    @header_decorator("МОНИТОРИНГ РЕСУРСОВ")
    def monitor_resources(self):
        print("1. Мониторинг всех процессов (топ по CPU)")
        print("2. Мониторинг конкретного процесса")
        
        choice = input("Выбор (1-2): ").strip()
        
        if choice == "1":
            self._monitor_all()
        elif choice == "2":
            self._monitor_specific()
        else:
            print("Неверный выбор")
    
    def _monitor_all(self):
        print("\nМониторинг топ-5 процессов по CPU (5 секунд)")
        print(f"{'Время':<8} {'PID':<8} {'Имя':<15} {'CPU%':<8} {'Память%':<10}")
        print("-" * 60)
        
        for second in range(5):
            processes = []
            for proc in process_generator():
                processes.append(proc)
            
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            
            print(f"\n{second+1} сек:")
            for i in range(min(5, len(processes))):
                p = processes[i]
                print(f"{'':<8} {p.pid:<8} {p.name[:15]:<15} {p.cpu_percent:<8.1f} {p.memory_percent:<10.2f}")
            
            if second < 4:
                time.sleep(1)
    
    def _monitor_specific(self):
        try:
            pid = int(input("\nВведите PID процесса: ").strip())
            
            print(f"\nМониторинг процесса {pid} (10 секунд)")
            print(f"{'Время':<8} {'CPU%':<8} {'Память%':<10} {'Память (MB)':<12}")
            print("-" * 60)
            
            for i in range(10):
                try:
                    proc = psutil.Process(pid)
                    cpu = proc.cpu_percent(interval=1)
                    mem_percent = proc.memory_percent()
                    mem_mb = proc.memory_info().rss // (1024 * 1024)
                    
                    print(f"{i+1} сек:{'':<4} {cpu:<8.1f} {mem_percent:<10.2f} {mem_mb:<12}")
                except psutil.NoSuchProcess:
                    print(f"\nПроцесс {pid} завершен")
                    break
                except:
                    print(f"\nОшибка мониторинга")
                    break
                    
        except ValueError:
            print("PID должен быть числом")

def main():
    manager = ProcessManager()
    
    while True:
        print("\n" + "=" * 50)
        print("УПРАВЛЕНИЕ ПРОЦЕССАМИ")
        print("=" * 50)
        print("1. Показать все процессы")
        print("2. Завершить процесс")
        print("3. Мониторинг ресурсов")
        print("4. Выход")
        
        choice = input("\nВыбор (1-4): ").strip()
        
        if choice == "1":
            manager.show_all_processes()
        elif choice == "2":
            manager.kill_process()
        elif choice == "3":
            manager.monitor_resources()
        elif choice == "4":
            print("\nВыход из программы")
            break
        else:
            print("\nНеверный выбор")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
