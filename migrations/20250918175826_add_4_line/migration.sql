-- AlterTable
ALTER TABLE "simmachine_selection" ADD COLUMN     "cpu" TEXT NOT NULL DEFAULT 'default_cpu_value',
ADD COLUMN     "hardDisk" TEXT NOT NULL DEFAULT 'default_hard_disk_value',
ADD COLUMN     "memory" TEXT NOT NULL DEFAULT 'default_memory_value',
ADD COLUMN     "slots" TEXT NOT NULL DEFAULT 'default_slots_value';
