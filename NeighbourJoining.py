#!/usr/bin/env python3
# -*- coding: utf-8 -*

from __future__ import division
import numpy as np
from Node import Node
from ete3 import Tree
from Tree import Tree

class NeighbourJoining():
	'''
	Phylogenetic tree reconstrution class
	'''
	def __init__(self, labels, sequences):
		self.nodes = [] 
		self.labels = labels #  sequence names
		self.sequences = sequences

	def execute(self):
		tree = Tree() # Set of functions for building the tree
		tree.normalizesMatrix(self.sequences)
		tree.generateMatrixDistances()
		self.d = tree.d #Distance matrix

		#Difecen Matrix
		self.d = [
		   # A  B  C  D  E  F
			[0, 0, 0, 0, 0, 0],	#A
			[5, 0, 0, 0, 0, 0],	#B
			[4, 7, 0, 0, 0, 0],	#C
			[7, 10, 7, 0, 0, 0],#D
			[6, 9, 6, 5, 0, 0],	#E
			[8, 11, 8, 9, 8, 0] #F
		]

		self.n = len(self.d[0])
		self.mappedPositions = [i for i in range(0, self.n)] #Mapped nodes positions
		print("Mapped positions: "+str(self.mappedPositions))

		cont = 1 #Number of the node to calculate
		while self.n > 2:
			self.differenceMatrix()
			self.stepOne()
			self.stepTwo()
			self.stepThree()
			self.stepFour()
			self.stepFive(cont)
			cont += 1

		print("Nodes: "+str(self.nodes))

	'''
	Computes the difference matrix
	'''
	def differenceMatrix(self):
		#Quantidade de Linhas/Colunas
		self.TAM = len(self.d[0]) #Matrix size

	'''
	Sums all distances from sequences 	
	'''
	def sumAllDistances(self, col):
		sumRow = 0
		sumCol = 0

		for i in range(0,col):
			sumRow += self.d[col][i]

		for j in range(col+1,self.TAM):
			sumCol += self.d[j][col]
			
		return (sumRow + sumCol)

	'''
	Find the smaller element in the matrix
	'''
	def minMatrix(self):
		minimum = 10000
		self.min = np.zeros(2).astype(int)
		for i in range(1,self.TAM):
			for j in range(0,self.TAM-1):
				if j < i and self.m[i][j] < minimum:
					minimum = self.m[i][j]
					self.min[0] = i
					self.min[1] = j

	'''
	Compute the net divergence r for every endonde(N = 6)
	'''
	def stepOne(self):
		self.r = [] #Compute the net divergence r
		for i in range(0,self.TAM):
			self.r.append(self.sumAllDistances(i))

	'''
	Create a rate-corrected distance matrix;
	The elements are defined by Mi = dij - (ri+rj)/(N-2)
	'''
	def stepTwo(self):
		self.m = np.zeros([self.TAM, self.TAM]) #M matrix

		for i in range(1,self.TAM):
			for j in range(0,self.TAM-1):
				if j < i:
					self.m[i][j] = self.d[i][j] - (self.r[i] + self.r[j])/(self.TAM-2)

	'''
	Define a new node that groups OTUs(Operational Taxonomic Units) i and j for which Mj is minimal
	'''
	def stepThree(self):
		self.minMatrix()

	'''
	Compute the branch lenghts from node U to A and B
	'''
	def stepFour(self):
		print("\nStep Four")
		p1 = self.d[self.min[0]][self.min[1]]

		#Compute the branch lengths from node U
		sumU1 = p1/2 + (self.r[0] - self.r[1])/(2*(self.TAM-2))
		sumU2 = p1 - sumU1
		
		print("Sau1: %s\nSbu1: %s" %(sumU1, sumU2))
		
		distances = [sumU1,sumU2]
		positions = [self.min[0], self.min[1]]
		self.node = Node(distances, positions) #Stores computed nodes

	'''
	Step Five com problemas
	Cont = Counter of the U-node to be calculated
	'''
	def stepFive(self, cont):
		print("\nStep Five")
		self.diu = [] #Compute new distances from node U to each other terminal node 

		dAB = self.d[self.min[0]][self.min[1]]
		for i in range(1,self.TAM):
			if i != self.min[0] and i != self.min[1]:
				# Diu = (dAi + dBi - dAB)/2
				dAi = self.d[i][self.min[1]]
				dBi = self.d[i][self.min[0]]
				self.diu.append((dAi + dBi - dAB)/2)
		
		'''
		New matrix size (self.TAM-1)
		'''
		self.modifiedDistanceMatrix = np.zeros([self.TAM-1, self.TAM-1])
		
		'''
		Create matrix Mx1 which stores U values
		x (line) and 1 (column)
		'''
		self.columnU = np.zeros([self.TAM-1, 1])

		for i in range(0, len(self.diu)):
			self.modifiedDistanceMatrix[i+1][0] = self.diu[i]

		if len(self.diu) > 2:
			for i in range(1, len(self.modifiedDistanceMatrix)):
				self.columnU[i][0] = self.diu[i-1]
		
		print(self.n)
		print(self.columnU)

		self.dx = np.delete(self.d,self.node.uPositions[0], 1)
		self.dx = np.delete(self.dx,self.node.uPositions[1], 1)
		

		self.dx = np.delete(self.dx,0,0)

		#print(self.dx)
		for i in range(1, len(self.modifiedDistanceMatrix)):
			for j in range(len(self.modifiedDistanceMatrix)-1):
				if j == 0:
					self.modifiedDistanceMatrix[i][j] = self.columnU[i][j]
				elif i <= len(self.modifiedDistanceMatrix):
					self.modifiedDistanceMatrix[i][j] = self.dx[i][j-1]
		
		print(self.n)
		print(self.modifiedDistanceMatrix)
		self.nodes.append([self.mappedPositions[self.node.uPositions[1]],self.mappedPositions[self.node.uPositions[0]]])
		#self.nodes.append(self.node.__dict__)
		self.d = self.modifiedDistanceMatrix
		#print(self.modifiedDistanceMatrix)
		self.n = self.n -1

		auxPosit = [cont*-1,]
		for i in range(0,self.TAM):
			if i != self.min[0] and i != self.min[1]:
				auxPosit.append(self.mappedPositions[i])

		self.mappedPositions = auxPosit
		print("positions: "+str(self.mappedPositions))

		'''
		A = np.delete(A, 1, 0)  # delete second row of A
		B = np.delete(B, 2, 0)  # delete third row of B
		C = np.delete(C, 1, 1)  # delete second column of C
		'''