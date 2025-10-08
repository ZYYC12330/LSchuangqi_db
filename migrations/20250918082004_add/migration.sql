/*
  Warnings:

  - You are about to drop the `iocardselection` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `simulationmachineselection` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "iocardselection";

-- DropTable
DROP TABLE "simulationmachineselection";

-- CreateTable
CREATE TABLE "iocard_selection" (
    "id" TEXT NOT NULL,
    "category" TEXT,
    "type" TEXT,
    "model" TEXT,
    "brief_description" TEXT NOT NULL,
    "detailed_description" TEXT NOT NULL,
    "brand" TEXT NOT NULL,
    "price_cny" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "total_amount_cny" TEXT NOT NULL,
    "supported_series" TEXT NOT NULL,

    CONSTRAINT "iocard_selection_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "simmachine_selection" (
    "id" TEXT NOT NULL,
    "category" TEXT,
    "type" TEXT,
    "model" TEXT,
    "brief_description" TEXT NOT NULL,
    "detailed_description" TEXT NOT NULL,
    "manufacturer" TEXT NOT NULL,
    "price_cny" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "total_amount_cny" TEXT NOT NULL,
    "series" TEXT NOT NULL,

    CONSTRAINT "simmachine_selection_pkey" PRIMARY KEY ("id")
);
