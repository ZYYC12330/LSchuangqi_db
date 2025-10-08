/*
  Warnings:

  - Changed the type of `price_cny` on the `iocard_selection` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.
  - Changed the type of `total_amount_cny` on the `iocard_selection` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.
  - Changed the type of `price_cny` on the `simmachine_selection` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.
  - Changed the type of `total_amount_cny` on the `simmachine_selection` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.

*/
-- AlterTable
ALTER TABLE "iocard_selection" ADD COLUMN     "channelCount" INTEGER,
ADD COLUMN     "currentRangeMax" DOUBLE PRECISION,
ADD COLUMN     "currentRangeMin" DOUBLE PRECISION,
ADD COLUMN     "highLevelMaxVoltage" DOUBLE PRECISION,
ADD COLUMN     "highLevelMinVoltage" DOUBLE PRECISION,
ADD COLUMN     "isCurrent" BOOLEAN,
ADD COLUMN     "isOutput" BOOLEAN,
ADD COLUMN     "lowLevelMaxVoltage" DOUBLE PRECISION,
ADD COLUMN     "lowLevelMinVoltage" DOUBLE PRECISION,
ADD COLUMN     "maxBaudRate" INTEGER,
ADD COLUMN     "resistanceRangeMax" DOUBLE PRECISION,
ADD COLUMN     "resistanceRangeMin" DOUBLE PRECISION,
ADD COLUMN     "resistanceResolution" INTEGER,
ADD COLUMN     "resolution" INTEGER,
ADD COLUMN     "sampleRate" DOUBLE PRECISION,
ADD COLUMN     "supportsCAN20A_B" BOOLEAN DEFAULT false,
ADD COLUMN     "supportsFlexibleInputModes" BOOLEAN,
ADD COLUMN     "supportsRS232" BOOLEAN DEFAULT false,
ADD COLUMN     "supportsRS422" BOOLEAN DEFAULT false,
ADD COLUMN     "supportsRS485" BOOLEAN DEFAULT false,
ADD COLUMN     "voltageRangeMax" DOUBLE PRECISION,
ADD COLUMN     "voltageRangeMin" DOUBLE PRECISION,
DROP COLUMN "price_cny",
ADD COLUMN     "price_cny" DECIMAL(65,30) NOT NULL,
DROP COLUMN "total_amount_cny",
ADD COLUMN     "total_amount_cny" DECIMAL(65,30) NOT NULL;

-- AlterTable
ALTER TABLE "simmachine_selection" DROP COLUMN "price_cny",
ADD COLUMN     "price_cny" DECIMAL(65,30) NOT NULL,
DROP COLUMN "total_amount_cny",
ADD COLUMN     "total_amount_cny" DECIMAL(65,30) NOT NULL;
