"use client";
import {
  Box,
  Button,
  chakra,
  CloseButton,
  Flex,
  Heading,
  HStack,
  IconButton,
  VisuallyHidden,
  VStack,
} from "@chakra-ui/react";
import { useDisclosure } from "@chakra-ui/react";
import Link from "next/link";

import React from "react";
import { AiOutlineMenu } from "react-icons/ai";

const NavBar = () => {
  const mobileNav = useDisclosure();
  return (
    <React.Fragment>
      <chakra.header
        bg="white"
        w="full"
        px={{
          base: 4,
          sm: 8,
        }}
        py={8}>
        <Flex
          p={4}
          rounded="lg"
          border="2px dashed black"
          alignItems="center"
          justifyContent="space-between"
          mx="auto">
          <Flex>
            <chakra.a
              href="/"
              title="Choc Home Page"
              display="flex"
              alignItems="center">
              <VisuallyHidden>Choc</VisuallyHidden>
            </chakra.a>
            <Heading fontSize="xl" ml="2">
              VaxMisinfo Youtube
            </Heading>
          </Flex>
          <HStack display="flex" alignItems="center" spacing={1}>
            <HStack
              spacing={1}
              mr={1}
              color="brand.500"
              display={{
                base: "none",
                md: "inline-flex",
              }}>
              <Link href="/">
                <Button variant="outline" colorScheme="black">
                  Home
                </Button>
              </Link>
              <Link href="/video-metrics">
                <Button variant="outline" colorScheme="black">
                  Analysis
                </Button>
              </Link>
              <Button variant="ghost">Contact</Button>
            </HStack>
            <Button colorScheme="brand" size="sm">
              Get Started
            </Button>
            <Box
              display={{
                base: "inline-flex",
                md: "none",
              }}>
              <IconButton
                display={{
                  base: "flex",
                  md: "none",
                }}
                aria-label="Open menu"
                fontSize="20px"
                color="gray.800"
                _dark={{
                  color: "inherit",
                }}
                variant="ghost"
                icon={<AiOutlineMenu />}
                onClick={mobileNav.onOpen}
              />

              <VStack
                pos="absolute"
                top={0}
                left={0}
                right={0}
                display={mobileNav.isOpen ? "flex" : "none"}
                flexDirection="column"
                p={2}
                pb={4}
                m={2}
                bg="white"
                spacing={3}
                rounded="sm"
                shadow="sm">
                <CloseButton
                  aria-label="Close menu"
                  onClick={mobileNav.onClose}
                />

                <Link href="/">
                  <Button variant="outline" colorScheme="black">
                    Home
                  </Button>
                </Link>
                <Link href="/video-metrics">
                  <Button variant="outline" colorScheme="black">
                    Analysis
                  </Button>
                </Link>
                <Button w="full" variant="ghost">
                  Contact
                </Button>
              </VStack>
            </Box>
          </HStack>
        </Flex>
      </chakra.header>
    </React.Fragment>
  );
};

export default NavBar;
