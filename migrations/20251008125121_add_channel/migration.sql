/*
  Warnings:

  - You are about to drop the column `channelCount` on the `iocard_selection` table. All the data in the column will be lost.
  - You are about to drop the column `remark` on the `iocard_selection` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "iocard_selection" DROP COLUMN "channelCount",
DROP COLUMN "remark",
ADD COLUMN     "afdxChannels" INTEGER,
ADD COLUMN     "analogInputChannels" INTEGER,
ADD COLUMN     "analogOutputChannels" INTEGER,
ADD COLUMN     "bissCChannels" INTEGER,
ADD COLUMN     "canBusChannels" INTEGER,
ADD COLUMN     "digitalIOChannels" INTEGER,
ADD COLUMN     "digitalInputChannels" INTEGER,
ADD COLUMN     "digitalOutputChannels" INTEGER,
ADD COLUMN     "encoderChannels" INTEGER,
ADD COLUMN     "i2cBusChannels" INTEGER,
ADD COLUMN     "pcmLvdChannels" INTEGER,
ADD COLUMN     "ppsPulseChannels" INTEGER,
ADD COLUMN     "pwmOutputChannels" INTEGER,
ADD COLUMN     "rtdResistanceChannels" INTEGER,
ADD COLUMN     "serialPortChannels" INTEGER,
ADD COLUMN     "spiBusChannels" INTEGER,
ADD COLUMN     "ssiBusChannels" INTEGER;
