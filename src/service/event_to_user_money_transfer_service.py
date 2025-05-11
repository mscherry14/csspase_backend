# async def transfer_money(session, from_acc, to_acc, amount):
#     async with session.start_transaction():
#         # Списание
#         await from_collection.
#         await from_collection.update_one(
#             {"_id": from_acc, "balance": {"$gte": amount}},
#             {"$inc": {"balance": -amount}},
#             session=session,
#         )
#         # Зачисление
#         await to_collection.update_one(
#             {"_id": to_acc},
#             {"$inc": {"balance": amount}},
#             session=session,
#         )