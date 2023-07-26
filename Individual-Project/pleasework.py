import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import pinecone
from sklearn.metrics.pairwise import cosine_similarity
# Load pre-trained SqueezeNet
squeezenet = models.squeezenet1_0(pretrained=True)

# Remove the classification head (final fully connected layers)
squeezenet = nn.Sequential(*list(squeezenet.children())[:-1])

# Set the model to evaluation mode (important for correct feature extraction)
squeezenet.eval()

# Function to extract embeddings from an image
def extract_embedding_for_pinecone(image_path):
    image = Image.open(image_path).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize(64),
        transforms.CenterCrop(64),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    input_image = preprocess(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output = squeezenet(input_image)
        embedding = output.squeeze().numpy()
    embedding1 = embedding.flatten()
    embedding2 = []
    for i in embedding1:
        embedding2.append(i.item())
    return embedding2



def extract_embedding(image_path):
    image = Image.open(image_path).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(256),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    input_image = preprocess(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output = squeezenet(input_image)
        embedding = output.squeeze().numpy()
    embedding1 = embedding.flatten()
    embedding2 = []
    for i in embedding1:
        embedding2.append(i.item())
    return embedding2

# directory_path = 'Dataset/Dataset/Bill_Gates'
#
# vectors= []
# a = 0
# for file in os.listdir(directory_path):
#     print(file)
#
#     vectors.append(('' + str(a) , list(extract_embedding(directory_path + '/' + file))))
#     a = a + 1
#     if a > 100:
#         break




# print(vectors)








def apiQuery(filename):
    pinecone.init(
	    api_key='ea812dbf-9c5e-4aee-95fe-c928a3cc3916',
	    environment='us-west4-gcp-free'
    )
    index = pinecone.Index('pleasework')
    vector = extract_embedding_for_pinecone(filename)
    vec = index.query(
        vector=vector,
        top_k=10,
        include_values=False,
        namespace='myfirstnamespace'
    )
    avg = []
    for match in vec['matches']:
        avg.append(match['score'])

    return (sum(avg) / len(avg)) * 100

# print(apiQuery())
def compare_two_images(filename1 , filename2):
    vector1 = np.array(extract_embedding(filename1)).reshape(1,-1)
    vector2 = np.array(extract_embedding(filename2)).reshape(1,-1)
    return cosine_similarity(vector1 , vector2)[0].item() * 100

# index.upsert(vectors=vectors , namespace='myfirstnamespace')
#
# vec = index.query(
#     vector=bec,
#     top_k=10,
#     include_values=True,
#     namespace='myfirstnamespace'
# )















