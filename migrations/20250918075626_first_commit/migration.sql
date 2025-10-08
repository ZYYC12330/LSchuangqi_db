-- CreateTable
CREATE TABLE "iocardselection" (
    "id" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "model" TEXT NOT NULL,
    "brief_description" TEXT NOT NULL,
    "detailed_description" TEXT NOT NULL,
    "brand" TEXT NOT NULL,
    "price_cny" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "total_amount_cny" TEXT NOT NULL,
    "supported_series" TEXT NOT NULL,

    CONSTRAINT "iocardselection_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "simulationmachineselection" (
    "id" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "model" TEXT NOT NULL,
    "brief_description" TEXT NOT NULL,
    "detailed_description" TEXT NOT NULL,
    "manufacturer" TEXT NOT NULL,
    "price_cny" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "total_amount_cny" TEXT NOT NULL,
    "series" TEXT NOT NULL,

    CONSTRAINT "simulationmachineselection_pkey" PRIMARY KEY ("id")
);
