-- AlterTable
ALTER TABLE "iocardselection" ALTER COLUMN "category" DROP NOT NULL,
ALTER COLUMN "model" DROP NOT NULL;

-- AlterTable
ALTER TABLE "simulationmachineselection" ALTER COLUMN "category" DROP NOT NULL,
ALTER COLUMN "model" DROP NOT NULL;
