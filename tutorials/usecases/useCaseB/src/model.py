import torch
import torch.nn as nn
import math 
import torch.nn.functional as F

class ESRT(nn.Module):
	def __init__(self, upscale=2, in_channels=4):
		# super(ESRT, self).__init__()
		super().__init__()
		
		wn = lambda x: torch.nn.utils.weight_norm(x)
		
		n_feats = 32
		n_blocks = 1
		kernel_size = 3

		self.n_blocks = n_blocks
		
		# define head module
		modules_head = [conv(in_channels, n_feats, kernel_size)]
		
		# define body module
		modules_body = nn.ModuleList()
		for i in range(n_blocks):
			modules_body.append(Un(n_feats=n_feats, wn = wn))

		# define tail module
		modules_tail = [
			Upsampler(conv, upscale, n_feats, act=False),
			conv(n_feats, in_channels, kernel_size)
		]


		self.head = nn.Sequential(*modules_head)
		self.body = nn.Sequential(*modules_body)
		self.reduce = conv(n_blocks*n_feats, n_feats, kernel_size)
		self.tail = nn.Sequential(*modules_tail)
		self.up = nn.Sequential(
			Upsampler(conv,upscale,n_feats,act=False),
			conv(n_feats, in_channels, 3,1,1)
		)

	def forward(self, x):
		x = self.head(x)
		res2 = x
		body_out = []
		for i in range(self.n_blocks):
			x = self.body[i](x)
			body_out.append(x)
		res1 = torch.cat(body_out,1)
		res1 = self.reduce(res1)
		x = self.tail(res1)
		x = self.up(res2) + x
		return x
	
	def load_state_dict(self, state_dict, strict=False):
		own_state = self.state_dict()
		for name, param in state_dict.items():
			if name in own_state:
				if isinstance(param, nn.Parameter):
					param = param.data
				# If dimensions match, copy weights
				if own_state[name].size() == param.size():
					own_state[name].copy_(param)
				else:
					# If it's 'up' or 'tail', skip so those layers train from scratch
					if name.find('up') >= 0 or name.find('tail') >= 0:
						print(f'Skipping loading weights for "{name}" due to shape mismatch. Training from scratch...')
						continue
					else:
						raise RuntimeError(
							f'While copying the parameter named {name}, '
							f'whose dimensions in the model are {own_state[name].size()} and '
							f'whose dimensions in the checkpoint are {param.size()}.')
			elif strict:
				if name.find('tail') == -1 and name.find('up') == -1:
					raise KeyError(f'unexpected key "{name}" in state_dict')
		if strict:
			missing = set(own_state.keys()) - set(state_dict.keys())
			if len(missing) > 0:
				raise KeyError(f'missing keys in state_dict: "{missing}"')
	
def conv(in_channels, out_channels, kernel_size, bias=True, groups = 1):
	wn = lambda x: torch.nn.utils.weight_norm(x)
	return nn.Conv2d(
		in_channels, out_channels, kernel_size,
		padding=(kernel_size//2), bias=bias, groups = groups
	)

class Un(nn.Module):
	def __init__(self,n_feats, wn):
		super(Un, self).__init__()
		self.encoder1 = Updownblock(n_feats)
		self.encoder2 = Updownblock(n_feats)
		self.encoder3 = Updownblock(n_feats)
		self.reduce = conv(3*n_feats, n_feats, 3)
		self.weight2 = Scale(1)
		self.weight1 = Scale(1)
		self.attention = MLABlock(n_feat=n_feats, dim=288) 
		self.alise = conv(n_feats, n_feats, 3)

	def forward(self,x):
		# out = self.encoder3(self.encoder2(self.encoder1(x)))
		x1 = self.encoder1(x)
		x2 = self.encoder2(x1)
		x3 = self.encoder3(x2)
		out = x3
		b,c,h,w = x3.shape
		out = self.attention(self.reduce(torch.cat([x1,x2,x3],dim=1)))
		out = out.permute(0,2,1)
		out = reverse_patches(out, (h,w), (3,3), 1, 1)
		out = self.alise(out)

		return self.weight1(x) + self.weight2(out)
	
class Scale(nn.Module):

	def __init__(self, init_value=1e-3):
		super().__init__()
		self.scale = nn.Parameter(torch.FloatTensor([init_value]))

	def forward(self, input):
		return input * self.scale
	
class Upsampler(nn.Sequential):
	def __init__(self, conv, scale, n_feats, bn=False, act=False, bias=True):
		m = []
		
		# Handle scale factor as product of smaller factors
		if scale == 10:
			# First upscale by 2
			m.append(conv(n_feats, 4 * n_feats, 3, bias))
			m.append(nn.PixelShuffle(2))
			if bn: m.append(nn.BatchNorm2d(n_feats))
			if act == 'relu': m.append(nn.ReLU(True))
			elif act == 'prelu': m.append(nn.PReLU(n_feats))
			
			# Then upscale by 5
			m.append(conv(n_feats, 25 * n_feats, 3, bias))
			m.append(nn.PixelShuffle(5))
			if bn: m.append(nn.BatchNorm2d(n_feats))
			if act == 'relu': m.append(nn.ReLU(True))
			elif act == 'prelu': m.append(nn.PReLU(n_feats))
			
		elif (scale & (scale - 1)) == 0:    # Is scale = 2^n?
			for _ in range(int(math.log(scale, 2))):
				m.append(conv(n_feats, 4 * n_feats, 3, bias))
				m.append(nn.PixelShuffle(2))
				if bn: m.append(nn.BatchNorm2d(n_feats))
				if act == 'relu': m.append(nn.ReLU(True))
				elif act == 'prelu': m.append(nn.PReLU(n_feats))

		elif scale == 3:
			m.append(conv(n_feats, 9 * n_feats, 3, bias))
			m.append(nn.PixelShuffle(3))
			if bn: m.append(nn.BatchNorm2d(n_feats))
			if act == 'relu': m.append(nn.ReLU(True))
			elif act == 'prelu': m.append(nn.PReLU(n_feats))
			
		elif scale == 5:
			m.append(conv(n_feats, 25 * n_feats, 3, bias))
			m.append(nn.PixelShuffle(5))
			if bn: m.append(nn.BatchNorm2d(n_feats))
			if act == 'relu': m.append(nn.ReLU(True))
			elif act == 'prelu': m.append(nn.PReLU(n_feats))
			
		else:
			raise NotImplementedError(f"Scale factor {scale} is not supported")

		super(Upsampler, self).__init__(*m)

class Updownblock(nn.Module):
	def __init__(self, n_feats):
		super(Updownblock, self).__init__()
		self.encoder = one_module(n_feats)
		self.decoder_low = one_module(n_feats) #nn.Sequential(one_module(n_feats),
		#                     one_module(n_feats),
		#                     one_module(n_feats))
		self.decoder_high = one_module(n_feats)
		self.alise = one_module(n_feats)
		self.alise2 = BasicConv(2*n_feats, n_feats, 1,1,0) #one_module(n_feats)
		self.down = nn.AvgPool2d(kernel_size=2)
		self.att = CALayer(n_feats)

	def forward(self, x):
		x1 = self.encoder(x)
		x2 = self.down(x1)
		high = x1 - F.interpolate(x2, size = x.size()[-2:], mode='bilinear', align_corners=True)
		for i in range(5):
			x2 = self.decoder_low(x2)
		x3 = x2
		# x3 = self.decoder_low(x2)
		high1 = self.decoder_high(high)
		x4 = F.interpolate(x3, size = x.size()[-2:], mode='bilinear', align_corners=True)
		return self.alise(self.att(self.alise2(torch.cat([x4,high1],dim=1))))+ x
	
class one_module(nn.Module):
	def __init__(self, n_feats):
		super(one_module, self).__init__()
		self.layer1 = one_conv(n_feats, n_feats//2,3)
		self.layer2 = one_conv(n_feats, n_feats//2,3)
		# self.layer3 = one_conv(n_feats, n_feats//2,3)
		self.layer4 = BasicConv(n_feats, n_feats, 3,1,1)
		self.alise = BasicConv(2*n_feats, n_feats, 1,1,0)
		self.atten = CALayer(n_feats)
		self.weight1 = Scale(1)
		self.weight2 = Scale(1)
		self.weight3 = Scale(1)
		self.weight4 = Scale(1)
		self.weight5 = Scale(1)

	def forward(self, x):

		x1 = self.layer1(x)
		x2 = self.layer2(x1)
		# x3 = self.layer3(x2)
		# pdb.set_trace()
		x4 = self.layer4(self.atten(self.alise(torch.cat([self.weight2(x2),self.weight3(x1)],1))))
		return self.weight4(x)+self.weight5(x4)
	
class BasicConv(nn.Module):
	def __init__(self, in_planes, out_planes, kernel_size, stride=1, padding=1, dilation=1, groups=1, relu=True,
				 bn=False, bias=False, up_size=0,fan=False):
		super(BasicConv, self).__init__()
		wn = lambda x:torch.nn.utils.weight_norm(x)
		self.out_channels = out_planes
		self.in_channels = in_planes
		if fan:
			self.conv = nn.ConvTranspose2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride, padding=padding,
							  dilation=dilation, groups=groups, bias=bias)
		else:
			self.conv = nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride, padding=padding,
							  dilation=dilation, groups=groups, bias=bias)
		self.bn = nn.BatchNorm2d(out_planes, eps=1e-5, momentum=0.01, affine=True) if bn else None
		self.relu = nn.ReLU(inplace=True) if relu else None
		self.up_size = up_size
		self.up_sample = nn.Upsample(size=(up_size, up_size), mode='bilinear') if up_size != 0 else None
		
	def forward(self, x):
		x = self.conv(x)
		if self.bn is not None:
			x = self.bn(x)
		if self.relu is not None:
			x = self.relu(x)
		if self.up_size > 0:
			x = self.up_sample(x)
		return x
	
class one_conv(nn.Module):
	def __init__(self,inchanels,growth_rate,kernel_size = 3, relu = True):
		super(one_conv,self).__init__()
		wn = lambda x:torch.nn.utils.weight_norm(x)
		self.conv = nn.Conv2d(inchanels,growth_rate,kernel_size=kernel_size,padding = kernel_size>>1,stride= 1)
		self.flag = relu
		self.conv1 = nn.Conv2d(growth_rate,inchanels,kernel_size=kernel_size,padding = kernel_size>>1,stride= 1)
		if relu:
			self.relu = nn.PReLU(growth_rate)
		self.weight1 = Scale(1)
		self.weight2 = Scale(1)
	def forward(self,x):
		if self.flag == False:
			output = self.weight1(x) + self.weight2(self.conv1(self.conv(x)))
		else:
			output = self.weight1(x) + self.weight2(self.conv1(self.relu(self.conv(x))))
		return output#torch.cat((x,output),1)
	
## Channel Attention (CA) Layer
class CALayer(nn.Module):
	def __init__(self, channel, reduction=16):
		super(CALayer, self).__init__()
		# global average pooling: feature --> point
		self.avg_pool = nn.AdaptiveAvgPool2d(1)
		# feature channel downscale and upscale --> channel weight
		self.conv_du = nn.Sequential(
				nn.Conv2d(channel, channel // reduction, 1, padding=0, bias=True),
				nn.ReLU(inplace=True),
				nn.Conv2d(channel // reduction, channel, 1, padding=0, bias=True),
				nn.Sigmoid()
		)

	def forward(self, x):
		y = self.avg_pool(x)
		y = self.conv_du(y)
		return x * y
	
class MLABlock(nn.Module):
	def __init__(
		self, n_feat = 64,dim=768, num_heads=8, mlp_ratio=4., qkv_bias=False, qk_scale=None, drop=0., attn_drop=0.,
				 drop_path=0., act_layer=nn.ReLU, norm_layer=nn.LayerNorm):
		super(MLABlock, self).__init__()
		self.dim = dim
		self.atten = EffAttention(self.dim, num_heads=8, qkv_bias=False, qk_scale=None, \
							 attn_drop=0., proj_drop=0.)
		self.norm1 = nn.LayerNorm(self.dim)
		# self.posi = PositionEmbeddingLearned(n_feat)
		self.mlp = Mlp(in_features=dim, hidden_features=dim//4, act_layer=act_layer, drop=drop)
		self.norm2 = nn.LayerNorm(self.dim)
	def forward(self, x):
		# pdb.set_trace()
		B = x.shape[0]
		# posi = self.posi(x)
		# x = posi + x
		# x = self.patch_embed(x) # 16*36*768
		# print(x.shape)
		x = extract_image_patches(x, ksizes=[3, 3],
									  strides=[1,1],
									  rates=[1, 1],
									  padding='same')#   16*2304*576
		x = x.permute(0,2,1)

		x = x + self.atten(self.norm1(x))
		x = x + self.mlp(self.norm2(x))#self.drop_path(self.mlp(self.norm2(x)))
		return x
	
class EffAttention(nn.Module):
	def __init__(self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0., proj_drop=0.):
		super().__init__()
		self.num_heads = num_heads
		head_dim = dim // num_heads
		# NOTE scale factor was wrong in my original version, can set manually to be compat with prev weights
		self.scale = qk_scale or head_dim ** -0.5

		self.reduce = nn.Linear(dim, dim//2, bias=qkv_bias)
		self.qkv = nn.Linear(dim//2, dim//2 * 3, bias=qkv_bias)
		self.proj = nn.Linear(dim//2, dim)
		self.attn_drop = nn.Dropout(attn_drop)
		# print('scale', self.scale)
		# print(dim)
		# print(dim//num_heads)
		# self.proj = nn.Linear(dim, dim)
		# self.proj_drop = nn.Dropout(proj_drop)

	def forward(self, x):
		x = self.reduce(x)
		B, N, C = x.shape
		# pdb.set_trace()
		qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
		# q = x.reshape(B, N, 1, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
		# k = x.reshape(B, N, 1, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
		# v = x.reshape(B, N, 1, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
		# qkv: 3*16*8*37*96
		q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
		# pdb.set_trace()
		
		q_all = torch.split(q, math.ceil(N//4), dim=-2)
		k_all = torch.split(k, math.ceil(N//4), dim=-2)
		v_all = torch.split(v, math.ceil(N//4), dim=-2)        

		output = []
		for q,k,v in zip(q_all, k_all, v_all):
			attn = (q @ k.transpose(-2, -1)) * self.scale   #16*8*37*37
			attn = attn.softmax(dim=-1)
			attn = self.attn_drop(attn)
			
			trans_x = (attn @ v).transpose(1, 2)#.reshape(B, N, C)

			output.append(trans_x)
		# pdb.set_trace()
		# attn = torch.cat(att, dim=-2)
		# x = (attn @ v).transpose(1, 2).reshape(B, N, C) #16*37*768
		x = torch.cat(output,dim=1)
		x = x.reshape(B,N,C)
		# pdb.set_trace()
		x = self.proj(x)
		# x = self.proj_drop(x)
		return x
	
class Mlp(nn.Module):
	def __init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.ReLU, drop=0.):
		super().__init__()
		out_features = out_features or in_features
		hidden_features = hidden_features or in_features//4
		self.fc1 = nn.Linear(in_features, hidden_features)
		self.act = act_layer()
		self.fc2 = nn.Linear(hidden_features, out_features)
		self.drop = nn.Dropout(drop)

	def forward(self, x):
		x = self.fc1(x)
		x = self.act(x)
		x = self.drop(x)
		x = self.fc2(x)
		x = self.drop(x)
		return x
	
def extract_image_patches(images, ksizes, strides, rates, padding='same'):
	"""
	Extract patches from images and put them in the C output dimension.
	:param padding:
	:param images: [batch, channels, in_rows, in_cols]. A 4-D Tensor with shape
	:param ksizes: [ksize_rows, ksize_cols]. The size of the sliding window for
	 each dimension of images
	:param strides: [stride_rows, stride_cols]
	:param rates: [dilation_rows, dilation_cols]
	:return: A Tensor
	"""
	assert len(images.size()) == 4
	assert padding in ['same', 'valid']
	batch_size, channel, height, width = images.size()
	
	if padding == 'same':
		images = same_padding(images, ksizes, strides, rates)
	elif padding == 'valid':
		pass
	else:
		raise NotImplementedError('Unsupported padding type: {}.\
				Only "same" or "valid" are supported.'.format(padding))

	unfold = torch.nn.Unfold(kernel_size=ksizes,
							 dilation=rates,
							 padding=0,
							 stride=strides)
	patches = unfold(images)
	return patches  # [N, C*k*k, L], L is the total number of such blocks

def reverse_patches(images, out_size, ksizes, strides, padding):
	"""
	Extract patches from images and put them in the C output dimension.
	:param padding:
	:param images: [batch, channels, in_rows, in_cols]. A 4-D Tensor with shape
	:param ksizes: [ksize_rows, ksize_cols]. The size of the sliding window for
	 each dimension of images
	:param strides: [stride_rows, stride_cols]
	:param rates: [dilation_rows, dilation_cols]
	:return: A Tensor
	"""
	unfold = torch.nn.Fold(output_size = out_size, 
							kernel_size=ksizes, 
							dilation=1, 
							padding=padding, 
							stride=strides)
	patches = unfold(images)
	return patches  # [N, C*k*k, L], L is the total number of such blocks

def same_padding(images, ksizes, strides, rates):
	assert len(images.size()) == 4
	batch_size, channel, rows, cols = images.size()
	out_rows = (rows + strides[0] - 1) // strides[0]
	out_cols = (cols + strides[1] - 1) // strides[1]
	effective_k_row = (ksizes[0] - 1) * rates[0] + 1
	effective_k_col = (ksizes[1] - 1) * rates[1] + 1
	padding_rows = max(0, (out_rows-1)*strides[0]+effective_k_row-rows)
	padding_cols = max(0, (out_cols-1)*strides[1]+effective_k_col-cols)
	# Pad the input
	padding_top = int(padding_rows / 2.)
	padding_left = int(padding_cols / 2.)
	padding_bottom = padding_rows - padding_top
	padding_right = padding_cols - padding_left
	paddings = (padding_left, padding_right, padding_top, padding_bottom)
	images = torch.nn.ZeroPad2d(paddings)(images)
	return images
