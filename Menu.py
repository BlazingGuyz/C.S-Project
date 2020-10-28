def BreakFast(Type):
	VegList=['Fresh Seasonal Cut Fruit Salad                              INR ', 'Fresh Fruit Salad with Mint and Lime                        INR ', 'BreakFast Cereals                                           INR ', 'Oatmeal Porridge with Flax Seed and Almonds                 INR ', 'Scrambled Tofu with Vegetables                              INR ', 'Plain or Masala Dosa                                        INR ', 'Bread Rack                                                  INR ', 'Steamed Idli                                                INR ', 'Uttapam                                                     INR ', 'Aloo Parantha                                               INR ']
	NonVegList=['White Omlette                                               INR ', 'Pancakes                                                    INR ', 'French Toast                                                INR ', 'Chicken Sausage                                             INR ']
	SeaFoodList=[]
	if Type=="Veg":
		return VegList
	elif Type=="NonVeg":
		return NonVegList
	elif Type=="SeaFood":
		return SeaFoodList

def All_Day(Type):
	VegList=['Paneer Wraps                                                INR ', 'Pav Bhaji                                                   INR ', 'Panne Arrabiata                                             INR ', 'Paneer Tikka Masala                                         INR ', 'Steamed Rice                                                INR ', 'Tawa Parantha                                               INR ', 'Gulab Jamun                                                 INR ', 'Rasmalai                                                    INR ', 'Choice of Ice Cream                                         INR ', 'Subz Biryani                                                INR ']
	NonVegList=['Grilled Chicken Sandwitch                                   INR ', 'Keema Pav                                                   INR ', 'Chicken Wraps                                               INR ', 'Spaghetti Bolognese                                         INR ', 'Chicken Tikka Masala                                        INR ', 'Chicken Biryani                                             INR ', 'Baked Bourbon Cheese Cake                                   INR ']
	SeaFoodList=['Fish and Chips                                              INR ', 'Crumb Fried Fish                                            INR ']
	if Type=="Veg":
		return VegList
	elif Type=="NonVeg":
		return NonVegList
	elif Type=="SeaFood":
		return SeaFoodList

def LunchandDinner(Type):
	VegList=['Goat Cheese Crostini                                        INR ', 'Refined Beans & Cheese Quesadilla                           INR ', 'Tandoori Malai Broccoli                                     INR ', 'Subz Seekh Kebab                                            INR ', 'Tandoori Aloo                                               INR ', 'Vegetarian Kebab Platter                                    INR ', 'Wild Mushroom Risotto                                       INR ', 'Panner Preparations(Butter/Mutter/Palak)                    INR ', 'Dal Tadka                                                   INR ', 'Dal Khichdi                                                 INR ', 'Steamed Rice                                                INR ', 'Flavoured Rice                                              INR ', 'Tandoori Roti                                               INR ', 'Plain/ Butter/ Garlic/ Chilli Garlic Naan                   INR ', 'Missi Roti                                                  INR ']
	NonVegList=['Frito Misto                                                 INR ', 'Chicken Tikka                                               INR ', 'Tandoori Chicken                                            INR ', 'Non Vegetarian Kebab Platter                                INR ', 'Fusilli Arrabiata with Chicken                              INR ', 'Lemon Chicken and Spinach Risotto                           INR ', 'New Zealand Lamb Chops                                      INR ', 'Fettuccine Alfredo                                          INR ', 'Chicken Preparations(Butter/Saagwala/Kadhai)                INR ', 'Mutton Dum Biryani                                          INR ']
	SeaFoodList=['Garlic Buttered Prawns                                      INR ', 'Fish Tikka                                                  INR ', 'Smoked Salmon Crostini                                      INR ', 'Fish Fingers                                                INR ', 'Grilled Prawns                                              INR ', 'Lobster Thermidor                                           INR ', 'Grilled Salmon                                              INR ', 'Prawn Agnolotti                                             INR ', 'Pan Seared Fish                                             INR ']
	if Type=="Veg":
		return VegList
	elif Type=="NonVeg":
		return NonVegList
	elif Type=="SeaFood":
		return SeaFoodList