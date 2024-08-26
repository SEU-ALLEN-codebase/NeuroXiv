import sqlite3


def create_indexes():
    conn = sqlite3.connect('../database/test_0410.db')
    c = conn.cursor()

    # Create indexes for the info table
    c.execute('CREATE INDEX IF NOT EXISTS idx_info_id ON info (ID);')
    c.execute('CREATE INDEX IF NOT EXISTS idx_info_celltype ON info (celltype);')
    c.execute('CREATE INDEX IF NOT EXISTS idx_info_brain_atlas ON info (brain_atlas);')

    # Create indexes for the Feature_Dendrite table
    c.execute('CREATE INDEX IF NOT EXISTS idx_feature_dendrite_id ON Feature_Dendrite (ID);')

    # Create indexes for the Feature_Axon table
    c.execute('CREATE INDEX IF NOT EXISTS idx_feature_axon_id ON Feature_Axon (ID);')

    # Create indexes for the Projection_Dendrite table
    c.execute('CREATE INDEX IF NOT EXISTS idx_projection_dendrite_id ON Projection_Dendrite (ID);')

    # Create indexes for the Projection_Axon table
    c.execute('CREATE INDEX IF NOT EXISTS idx_projection_axon_id ON Projection_Axon (ID);')

    # Create indexes for the Projection_All_Arbor table
    c.execute('CREATE INDEX IF NOT EXISTS idx_projection_all_arbor_id ON Projection_All_Arbor (ID);')

    conn.commit()
    conn.close()


# Call the function to create indexes
create_indexes()
