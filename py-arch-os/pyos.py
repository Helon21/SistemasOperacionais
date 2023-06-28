import curses
import pycfg

DEFAULT_PROCCESS = 'load default'
CLEAR_CONSOLE = 'clear'
EXIT_COMMAND = 'exit'

SYS_EXIT = 1

class os_t:
	def __init__ (self, cpu, memory, terminal):
		self.cpu = cpu
		self.memory = memory
		self.terminal = terminal

		self.terminal.enable_curses()

		self.console_str = ""

		self.current_process = None
		
	def printk(self, msg):
		self.terminal.kernel_print("kernel: " + msg + "\n")

	def panic (self, msg):
		self.terminal.end()
		self.terminal.dprint("kernel panic: " + msg)
		self.cpu.cpu_alive = False
		#cpu.cpu_alive = False

	def interrupt_keyboard (self):
		key = self.terminal.get_key_buffer()
		if ((key >= ord('a')) and (key <= ord('z'))) or ((key >= ord('A')) and (key <= ord('Z'))) or ((key >= ord('0')) and (key <= ord('9'))) or (key == ord(' ')) or (key == ord('-')) or (key == ord('_')) or (key == ord('.')):
			strchar = chr(key)
			self.terminal.console_print(strchar)
			self.console_str += strchar
		elif key == curses.KEY_BACKSPACE:
			if len(self.console_str) > 0:
				self.terminal.console_print("\r")
				self.console_str = self.console_str[:-1]
				self.terminal.console_print(self.console_str)
		elif (key == curses.KEY_ENTER) or (key == ord('\n')):
			self.verify_input()
			self.clear()	

	def handle_interrupt (self, interrupt):
		if pycfg.INTERRUPT_MEMORY_PROTECTION_FAULT == interrupt:
			self.printk("Memory Protection Fault Interruption not Implemented yet")
		elif pycfg.INTERRUPT_KEYBOARD == interrupt:
			self.keyboard_interrupt_detected()
		elif pycfg.INTERRUPT_TIMER == interrupt:
			self.printk("Timer Interruption not Implemented yet")

	def clear (self):
		self.terminal.console_print('\r')
		self.console_str = ''

	def keyboard_interrupt_detected(self):
		self.interrupt_keyboard()

	def verify_input(self):
		if(self.console_str == CLEAR_CONSOLE):
			self.terminal.app_print('\r')
		elif (self.console_str == EXIT_COMMAND):
			self.stop_execution()
		elif self.console_str == DEFAULT_PROCCESS:
			self.load_process()
		else:
			self.terminal.app_print('\n' + self.console_str)

	def stop_execution(self):
		self.panic("System interrupted by user")
	
	def create_process(self, pid, program):
		memory_start = 0
		memory_end = self.memory.size - 1
		new_process = Process(pid, "ready", memory_start, memory_end, program)
		self.current_process = new_process
		new_process.start()
	
	def load_process(self):
		self.terminal.app_print("\nLoading default process...")
		self.create_process(1, "default_program.bin")
		
	def syscall_exit(self):
		self.terminal.end()
		self.cpu.cpu_alive = False
		self.terminal.dprint("pysim halted")

	def syscall(self):
		syscall_code = self.cpu.get_reg(0)
		if syscall_code == SYS_EXIT:
			self.syscall_exit()
			

class Process:
    def __init__(self, pid, state, memory_start, memory_end, program):
        self.pid = pid
        self.state = state
        self.memory_start = memory_start
        self.memory_end = memory_end
        self.program = program

        self.pc = 0
        self.general_purpose_registers = [0] * 8

        self.memory_descriptors = []

        self.open_file_descriptors = []

        self.metadata = {"state": self.state}

    def __str__(self):
        return "Process: (PID: {}, State: {}, Memory Space: {}, Program: {})".format(self.pid, self.state, self.memory_space, self.program)

    def start(self):
       self.state = "running"

    def add_memory_descriptor(self, start_address, size):
        descriptor = {"start_address": start_address, "size": size}
        self.memory_descriptors.append(descriptor)

    def open_file(self, file_path, mode):
        file_descriptor = open(file_path, mode)
        self.open_file_descriptors.append(file_descriptor)
        return file_descriptor

    def close_file(self, file_descriptor):
        if file_descriptor in self.open_file_descriptors:
            file_descriptor.close()
            self.open_file_descriptors.remove(file_descriptor)

    def update_metadata(self, key, value):
        self.metadata[key] = value
