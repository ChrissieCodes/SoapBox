import unitofwork


def allocations(reference: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            """
            SELECT itemID, findItem, reference FROM recommendations WHERE reference = :reference
            """,
            dict(reference=reference),
        )
    return [dict(r) for r in results]