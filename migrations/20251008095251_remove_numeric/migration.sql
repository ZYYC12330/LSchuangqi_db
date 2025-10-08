/*
  Warnings:

  - You are about to alter the column `price_cny` on the `iocard_selection` table. The data in that column could be lost. The data in that column will be cast from `Decimal(65,30)` to `Integer`.
  - You are about to alter the column `total_amount_cny` on the `iocard_selection` table. The data in that column could be lost. The data in that column will be cast from `Decimal(65,30)` to `Integer`.
  - You are about to alter the column `price_cny` on the `simmachine_selection` table. The data in that column could be lost. The data in that column will be cast from `Decimal(65,30)` to `Integer`.
  - You are about to alter the column `total_amount_cny` on the `simmachine_selection` table. The data in that column could be lost. The data in that column will be cast from `Decimal(65,30)` to `Integer`.

*/
-- AlterTable
ALTER TABLE "iocard_selection" ALTER COLUMN "price_cny" SET DATA TYPE INTEGER,
ALTER COLUMN "total_amount_cny" SET DATA TYPE INTEGER;

-- AlterTable
ALTER TABLE "simmachine_selection" ALTER COLUMN "price_cny" SET DATA TYPE INTEGER,
ALTER COLUMN "total_amount_cny" SET DATA TYPE INTEGER;
