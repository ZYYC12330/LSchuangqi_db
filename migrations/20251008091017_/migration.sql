-- AlterTable
ALTER TABLE "iocard_selection" ALTER COLUMN "price_cny" DROP NOT NULL,
ALTER COLUMN "total_amount_cny" DROP NOT NULL;

-- AlterTable
ALTER TABLE "simmachine_selection" ALTER COLUMN "price_cny" DROP NOT NULL,
ALTER COLUMN "total_amount_cny" DROP NOT NULL;
