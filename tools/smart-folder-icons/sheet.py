import sys,glob,os
from PIL import Image
p,ext,root,out=sys.argv[1:5]; ex=sys.argv[5].split(',')
new=sorted(glob.glob(f'{root}/{p}/icons/smart-*.{ext}')); old=[f'{root}/{p}/icons/{n}.{ext}' for n in ex]
S=160; fs=new+old; cols=10; rows=(len(fs)+cols-1)//cols
sh=Image.new('RGB',(S*cols,S*rows),(110,110,118))
for k,f in enumerate(fs):
  im=Image.open(f).convert('RGBA'); im.thumbnail((S-8,S-8)); sh.paste(im,((k%cols)*S+4,(k//cols)*S+4),im)
os.makedirs(os.path.dirname(out),exist_ok=True); sh.save(out)
