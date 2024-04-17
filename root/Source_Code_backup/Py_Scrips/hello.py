import unreal

def listAssetPaths():
    EAL = unreal.EditorAssetLibrary
    
    assetPaths = EAL.list_assets("/All")
    
    for assetPath in assetPaths: print(assetPath)