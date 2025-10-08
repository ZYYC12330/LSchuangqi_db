/*
  Warnings:

  - You are about to drop the column `hardDisk` on the `simmachine_selection` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "simmachine_selection" DROP COLUMN "hardDisk",
ADD COLUMN     "hard_disk" TEXT DEFAULT 'default_hard_disk_value';
