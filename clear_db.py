import asyncio
from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()

async def main():
    db = Prisma()
    await db.connect()
    
    # 删除所有记录
    result = await db.iocard_selection.delete_many()
    print(f"已删除 {result} 条记录")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

