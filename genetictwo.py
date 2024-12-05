import random
import sqlite3
import tkinter as tk
from tkinter import ttk
import sqlite3

conn = sqlite3.connect ("database.db")
c = conn.cursor()
c.execute ("select * from courses")
courses = c.fetchall ()
c.execute ("select * from lecturers")
lecturers = c.fetchall ()
c.execute ("select * from rooms")
rooms = c.fetchall ()
c.execute ("select * from timeslots")
timeslots = c.fetchall ()
conn.commit()
# Define problem parameters
pop_size = 100
num_generations = 20
touranament_size = 5
mutation_rate = 0.05
"""
    Constraints:

    Hard Constraints (must be satisfied):
        No lecturer can teach more than one class at the same time.
        No room can host more than one class at the same time.
        A room's capacity must meet or exceed the number of students in the course.
        A student cannot attend two courses at the same time.
    Soft Constraints (preferences to optimize):
        Schedule lectures at preferred times for students or lecturers.
        Minimize gaps in the schedule for lecturers or students.
        Avoid late evening classes unless necessary.
"""

# Initial population
def create_chromosome():#list of genes(list of courses details)
    # Create a random timetable
    if (courses and lecturers and rooms and timeslots):
        return [[random.choice(courses), random.choice(lecturers), random.choice(rooms), random.choice(timeslots)]
                for _ in courses]

def create_population(size):#list of chromocomes (tables)
    return [create_chromosome() for _ in range(size)]

# Fitness function
def fitness(chromosome):
    HCV = 0  # Hard Constraint Violations
    SCV = 0  # Soft Constraint Violations

    course1, lecturer1, room1, timeslot1 = chromosome[0]
    # Check hard constraints
    for gene in chromosome:
        
        if gene is chromosome[0]:
            continue
        course, lecturer, room, timeslot = gene
        # Check if lecturer is already teaching at the same time
        
        if lecturer == lecturer1 and timeslot == timeslot1:
            HCV+=1
            #room can't host more than one class at the same time
        if room == room1 and timeslot == timeslot1:
            HCV+=1
            # Check if room's capacity meets or exceeds the number of students in the course
        if room[1]<=course[3]:
            HCV+=1
            # Check if student is already attending another course at the same time
        if course[2] == course1[2]:
            HCV+=1
        # Check soft constraints (there is gaps between classes)
        if timeslot [2]==timeslot1[2]:
            if (timeslot[1]==12 and timeslot[2]=="BM" )or(timeslot1[1]==12 and timeslot1[2]=="BM" ):
                if (timeslot[1]!=12 and timeslot[2]=="BM" )or(timeslot1[1]!=12 and timeslot1[2]=="BM"):
                    if timeslot[1]!=12 :
                        timeslot[1]+12
                        if abs(timeslot1[1]-timeslot[1])>=4:
                            SCV+=1
                    else:
                        timeslot1[1]+12
                        if abs(timeslot1[1]-timeslot[1])>=4:
                            SCV+=1

            if abs(timeslot[1]-timeslot1[1]):
                SCV+=1
        if timeslot [2]!=timeslot1[2]:
            if (timeslot[1]!=12 and timeslot[2]=="BM" )or(timeslot1[1]!=12 and timeslot1[2]=="BM"):
                x = abs(timeslot[1]-timeslot1[1])
                if abs(x-12)>=4:
                    SCV+=1
                            
        course1, lecturer1, room1, timeslot1 = gene
    return 1 / (1 + HCV + 0.5 * SCV)

# Genetic Operators
def crossover(parents,segment_lens):
    

    childs = []
    parent_count = len(parents)
    for j in range(parent_count):
        child = []
        start = 0
        for i, length in enumerate(segment_lens):
            parent_idx = i % parent_count  # Round-robin assignment
            child.extend(parents[(parent_idx+1) % parent_count][start:start + length])
            start += length
        childs.append(child)
    return childs


def mutate(chromosome):
    if random.random() < 0.05:  # Mutation rate
        gene_idx = random.randint(0, len(chromosome) - 1)
        chromosome[gene_idx][3] = random.choice(timeslots)  # Mutate timeslot
    return chromosome

# Genetic Algorithm
def genetic_algorithm(pop_size, generations):
    population = create_population(pop_size)
    for _ in range(generations):
        # Evaluate fitness
        population = sorted(population, key=lambda x: fitness(x), reverse=True) # sort the population based on fitness
        next_generation = population[:pop_size // 2] # select the top half of the population for the next generation

        # Apply crossover
        while len(next_generation) < pop_size:# ensure the next generation is full
            parents= random.sample(next_generation, touranament_size)# select two parents for crossover
            seg_lens = [2,1,1]
            childs = crossover(parents,seg_lens)
            for i in range(len(childs)):
                next_generation.append(mutate(childs[i]))
            

        population = next_generation

    return max(population, key=fitness)

# Run the algorithm
best_timetable = genetic_algorithm(pop_size=100, generations=500)
print("Best Timetable:", best_timetable)

conn.close()




